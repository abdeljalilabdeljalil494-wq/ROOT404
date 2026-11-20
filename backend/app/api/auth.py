from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.services.email import EmailDeliveryError
from app.core.database import get_db
from app.core.security import (
    generate_and_store_otp, verify_otp, create_access_token, get_last_otp,
    sanitize_input, validate_username, validate_email_format
)
from app.core.dependencies import get_current_user, auth_rate_limit
from app.core.config import settings
from app.models.user import User
from app.services.coalition import CoalitionService
from app.services.skill_graph import SkillGraphService
from datetime import timedelta
import logging
import re

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

class OtpRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254, description="Valid email address")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        v = v.lower().strip()
        if len(v) > settings.MAX_EMAIL_LENGTH:
            raise ValueError("Email too long")
        if ".." in v or v.startswith(".") or v.endswith("."):
            raise ValueError("Invalid email format")
        return v

class OtpVerify(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$', description="6-digit OTP code")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower().strip()

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Alphanumeric + _-")
    email: EmailStr = Field(..., max_length=254)
    display_name: str = Field(..., min_length=2, max_length=50)
    full_name: str = Field("", max_length=100)
    campus: str = Field("Tunis", max_length=20)
    
    @field_validator('username')
    @classmethod
    def validate_username_field(cls, v):
        v = v.strip().lower()
        valid, msg = validate_username(v)
        if not valid:
            raise ValueError(msg)
        return v
    
    @field_validator('display_name')
    @classmethod
    def sanitize_display_name(cls, v):
        v = sanitize_input(v, max_length=50)
        if len(v) < 2:
            raise ValueError("Display name too short")
        if not re.match(r'^[\w\s\-\.\']+$', v, re.UNICODE):
            raise ValueError("Display name contains invalid characters")
        return v
    
    @field_validator('full_name')
    @classmethod
    def sanitize_full_name(cls, v):
        if v:
            v = sanitize_input(v, max_length=100)
        return v
    
    @field_validator('campus')
    @classmethod
    def validate_campus(cls, v):
        if v not in settings.CAMPUSES:
            return settings.DEFAULT_CAMPUS
        return v

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)

@router.post("/otp", dependencies=[Depends(auth_rate_limit)])
def request_otp(payload: OtpRequest, request: Request, db: Session = Depends(get_db)):
    """Request OTP - rate limited, prevents email enumeration"""
    try:
        email = payload.email.lower().strip()
        
        valid, msg = validate_email_format(email)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)
        
        user_exists = db.query(User).filter(User.email == email).first() is not None
        
        try:
            otp = generate_and_store_otp(email)
        except ValueError as e:
            logger.warning(f"OTP rate limit exceeded for {email} from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(status_code=429, detail=str(e))
        
        logger.info(f"OTP generated for {email} (exists={user_exists}) from {request.client.host if request.client else 'unknown'}")
        
        response = {
            "sent": True,
            "email": email,
            "message": "OTP envoyé par email - vérifiez votre boîte de réception",
            "expires_in": settings.OTP_EXPIRE_MINUTES * 60
        }
        
        if settings.ENVIRONMENT == "development" and settings.ENABLE_DEV_OTP:
            response["dev_otp"] = otp
            response["dev_warning"] = "dev_otp only returned in development mode"
        
        return response
        
    except EmailDeliveryError:
        raise HTTPException(status_code=503, detail="Email delivery unavailable; retry requesting a code")
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in OTP request: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in OTP request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/verify", dependencies=[Depends(auth_rate_limit)])
def verify_otp_code(payload: OtpVerify, request: Request, db: Session = Depends(get_db)):
    """Verify OTP - rate limited, secure comparison"""
    try:
        email = payload.email.lower().strip()
        code = payload.code.strip()
        
        if not re.match(r'^\d{6}$', code):
            raise HTTPException(status_code=400, detail="Invalid OTP format")
        
        is_valid = verify_otp(email, code)
        
        if not is_valid:
            logger.warning(f"Invalid OTP attempt for {email} from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(status_code=400, detail="Code OTP invalide ou expiré")
        
        try:
            user = db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user {email}: {e}")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        if not user:
            logger.info(f"OTP verified but user not found: {email}")
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé, veuillez vous inscrire")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Compte désactivé ou gelé (Black Hole)")
        
        user.is_verified = True
        db.commit()
        token = create_access_token({"sub": user.id, "username": user.username, "sv": user.session_version})
        
        logger.info(f"User {user.username} logged in via OTP from {request.client.host if request.client else 'unknown'}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user.to_dict()
        }
        
    except EmailDeliveryError:
        raise HTTPException(status_code=503, detail="Email delivery unavailable; retry requesting a code")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OTP verify: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register", dependencies=[Depends(auth_rate_limit)])
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Register new user with strict validation"""
    try:
        try:
            existing_username = db.query(User).filter(User.username == payload.username.lower()).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
            
            existing_email = db.query(User).filter(User.email == payload.email.lower()).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="Email déjà utilisé")
        except SQLAlchemyError as e:
            logger.error(f"Database error checking existing user: {e}")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        campus = payload.campus if payload.campus in settings.CAMPUSES else settings.DEFAULT_CAMPUS
        
        user = User(
            username=payload.username.lower(),
            email=payload.email.lower(),
            display_name=sanitize_input(payload.display_name, max_length=50),
            full_name=sanitize_input(payload.full_name, max_length=100) if payload.full_name else "",
            campus=campus,
            level=0.0,
            xp=0,
            is_active=True,
            is_verified=False,
            skills=SkillGraphService.initialize_skills()
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating user: {e}")
            raise HTTPException(status_code=503, detail="Failed to create account")
        
        try:
            CoalitionService.assign_user_to_coalition(user, db)
        except Exception as e:
            logger.warning(f"Failed to assign coalition to {user.username}: {e}")
        
        try:
            otp = generate_and_store_otp(payload.email.lower())
        except ValueError as e:
            logger.warning(f"OTP rate limit after registration for {payload.email}: {e}")
            otp = None
        except EmailDeliveryError:
            raise
        except Exception:
            raise HTTPException(status_code=503, detail="Account created; retry requesting a code")
        
        logger.info(f"New user registered: {user.username} ({user.email}) from {request.client.host if request.client else 'unknown'}")
        
        response = {
            "message": "Compte créé avec succès, vérifiez votre email pour le code OTP",
            "user": user.to_dict(),
            "next_step": "verify_otp"
        }
        
        if settings.ENVIRONMENT == "development" and settings.ENABLE_DEV_OTP and otp:
            response["dev_otp"] = otp
        
        return response
        
    except EmailDeliveryError:
        raise HTTPException(status_code=503, detail="Email delivery unavailable; retry requesting a code")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in registration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", dependencies=[Depends(auth_rate_limit)])
def login_simple(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Simplified login - just email, sends OTP (rate limited via otp endpoint)"""
    return request_otp(OtpRequest(email=payload.email), request, db)

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@router.get("/me/full")
def get_me_full(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        from app.services.gamification import GamificationService, calculate_level_progress
        from app.services.skill_graph import SkillGraphService
        from app.services.integrity import IntegrityService
        
        from app.services.beta_progress import mission as current_mission
        mission = current_mission(db,current_user)

        try:
            skills = SkillGraphService.get_skill_graph_for_user(current_user)
            gaps = SkillGraphService.get_knowledge_gaps(current_user)
        except Exception as e:
            logger.warning(f"Failed to get skills for {current_user.username}: {e}")
            skills = []
            gaps = []
        
        try:
            integrity = IntegrityService.calculate_score(current_user, db)
        except Exception as e:
            logger.warning(f"Failed to calculate integrity for {current_user.username}: {e}")
            integrity = {"total": 100, "rows": []}
        
        try:
            streak_info = GamificationService.check_streak(current_user, db)
        except Exception as e:
            logger.warning(f"Failed to check streak for {current_user.username}: {e}")
            streak_info = {"streak": current_user.streak}
        
        base = current_user.to_dict()
        base.update({
            "levelProgress": calculate_level_progress(current_user.xp),
            "skills": skills,
            "knowledgeGaps": gaps,
            "integrity": integrity,
            "dailyMission": {**mission,"reward":mission['reward_xp'],"difficulty":1,"time":"UTC","skill":"Stream Sum — Python"},
            "streakInfo": streak_info
        })
        return base
    except Exception as e:
        logger.error(f"Error in get_me_full for {current_user.username}: {e}", exc_info=True)
        return current_user.to_dict()

@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.core.security import decode_token
    from app.models.auth_state import RevokedToken
    from datetime import datetime
    token = request.headers.get("authorization", "").split(" ", 1)[-1]
    payload = decode_token(token)
    db.merge(RevokedToken(jti=payload["jti"], expires_at=datetime.utcfromtimestamp(payload["exp"])))
    db.commit()
    return {"ok": True}
