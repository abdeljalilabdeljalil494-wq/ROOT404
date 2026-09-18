from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import generate_and_store_otp, verify_otp, create_access_token, get_last_otp
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.coalition import CoalitionService
from app.services.skill_graph import SkillGraphService
from datetime import timedelta
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])

class OtpRequest(BaseModel):
    email: EmailStr

class OtpVerify(BaseModel):
    email: EmailStr
    code: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    full_name: str = ""
    campus: str = "Tunis"

class LoginRequest(BaseModel):
    email: EmailStr

@router.post("/otp")
def request_otp(payload: OtpRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    # Generate OTP regardless (to prevent enumeration)
    otp = generate_and_store_otp(payload.email)
    
    # In dev, return OTP in response for testing
    # In prod, send via email
    return {
        "sent": True,
        "email": payload.email,
        "message": "OTP envoyé par email",
        "dev_otp": otp,  # Remove in production!
        "expires_in": 600
    }

@router.post("/verify")
def verify_otp_code(payload: OtpVerify, db: Session = Depends(get_db)):
    if not verify_otp(payload.email, payload.code):
        # For dev convenience, also check last OTP directly
        last = get_last_otp(payload.email)
        if not last or payload.code != last:
            raise HTTPException(status_code=400, detail="Code OTP invalide ou expiré")
    
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user:
        # Auto-create user for OTP flow? Or require registration
        # For this endpoint, we require existing user
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé, veuillez vous inscrire")
    
    # Create token
    token = create_access_token({"sub": user.id, "username": user.username})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Check existing
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Validate campus
    from app.core.config import settings
    campus = payload.campus if payload.campus in settings.CAMPUSES else settings.DEFAULT_CAMPUS
    
    user = User(
        username=payload.username.lower(),
        email=payload.email.lower(),
        display_name=payload.display_name,
        full_name=payload.full_name,
        campus=campus,
        level=0.0,
        xp=0,
        is_active=True,
        is_verified=False,
        skills=SkillGraphService.initialize_skills()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign to coalition
    try:
        CoalitionService.assign_user_to_coalition(user, db)
    except:
        pass
    
    # Generate OTP for verification
    otp = generate_and_store_otp(payload.email)
    
    return {
        "message": "Compte créé, vérifiez votre email",
        "user": user.to_dict(),
        "dev_otp": otp,
        "next_step": "verify_otp"
    }

@router.post("/login")
def login_simple(payload: LoginRequest, db: Session = Depends(get_db)):
    """Simplified login - just email, sends OTP"""
    return request_otp(OtpRequest(email=payload.email), db)

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@router.get("/me/full")
def get_me_full(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.gamification import GamificationService, xp_to_level, calculate_level_progress
    from app.services.skill_graph import SkillGraphService
    from app.services.integrity import IntegrityService
    from app.models import DailyMission
    
    # Get daily mission
    mission = GamificationService.generate_daily_mission(current_user, db)
    
    # Skill graph
    skills = SkillGraphService.get_skill_graph_for_user(current_user)
    gaps = SkillGraphService.get_knowledge_gaps(current_user)
    
    # Integrity
    integrity = IntegrityService.calculate_score(current_user, db)
    
    # Streak
    streak_info = GamificationService.check_streak(current_user, db)
    
    base = current_user.to_dict()
    base.update({
        "levelProgress": calculate_level_progress(current_user.xp),
        "skills": skills,
        "knowledgeGaps": gaps,
        "integrity": integrity,
        "dailyMission": {
            "title": mission.title if mission else "Reverse a linked list",
            "difficulty": mission.difficulty if mission else 3,
            "time": "~30 min",
            "reward": mission.reward_xp if mission else 120,
            "skill": mission.skill if mission else "Structures de données"
        },
        "streakInfo": streak_info
    })
    return base

@router.post("/logout")
def logout():
    # Client should delete token
    return {"ok": True, "message": "Déconnecté"}
