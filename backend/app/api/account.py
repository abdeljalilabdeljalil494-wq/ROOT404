"""Owner-only account privacy/export/deletion and all-session revocation."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.core.database import get_db, Base
from app.core.dependencies import get_current_user, auth_rate_limit, security
from fastapi.security import HTTPAuthorizationCredentials
from app.models.user import User

router = APIRouter(prefix='/account', tags=['Account & privacy'])


def recent_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    from app.core.security import decode_token
    payload = decode_token(credentials.credentials) if credentials else None
    if not payload or datetime.utcnow().timestamp() - payload['iat'] > 600:
        raise HTTPException(403, 'Recent sign-in required for this action (10 minutes)')


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    display_name: str = Field(min_length=1, max_length=50)
    bio: str = Field(default='', max_length=1000)


class Preferences(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    public_profile: bool
    directory_visible: bool


class DeleteConfirmation(BaseModel):
    confirmation: str = Field(max_length=254)


def prefs(user):
    return {'public_profile': user.public_profile, 'directory_visible': user.directory_visible}


@router.get('/privacy')
def privacy(user: User = Depends(get_current_user)):
    return prefs(user)


@router.put('/privacy', dependencies=[Depends(auth_rate_limit)])
def set_privacy(payload: Preferences, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.public_profile = payload.public_profile
    user.directory_visible = payload.directory_visible
    db.commit()
    return prefs(user)


@router.post('/sessions/revoke-all', dependencies=[Depends(auth_rate_limit)])
def revoke_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Atomic increment also serializes concurrent revocations on PostgreSQL.
    db.execute(update(User).where(User.id == user.id).values(session_version=User.session_version + 1))
    db.commit()
    return {'ok': True, 'detail': 'All sessions revoked; sign in again'}


@router.get('/export', dependencies=[Depends(auth_rate_limit), Depends(recent_auth)])
def export(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Export ONLY direct owned records, never co-members, other learners' code,
    # inbound messages, reviewer identities or peer private comments.
    profile = {column.name: getattr(user, column.name) for column in User.__table__.columns
               if column.name not in {'hashed_password', 'session_version'}}
    tables, total_bytes = {}, 0
    import json
    for name in ['submissions', 'user_project_progress', 'mentor_interactions', 'room_messages',
                 'mission_claims', 'moderation_reports', 'oauth_identities', 'notifications', 'room_members', 'daily_missions', 'user_badges', 'user_piscine_progress', 'coalition_members']:
        table = Base.metadata.tables[name]
        rows = db.execute(select(table).where(table.c.user_id == user.id).limit(10001)).mappings().yield_per(10)
        items = []
        for row in rows:
            item = jsonable_encoder(dict(row))
            if name == 'moderation_reports': item.pop('reviewer_id',None)
            total_bytes += len(json.dumps(item).encode())
            if len(items) >= 10000 or total_bytes > 16777216:
                raise HTTPException(413, 'Export exceeds synchronous limit; contact operator for private offline export')
            items.append(item)
        tables[name] = items
    return JSONResponse(jsonable_encoder({'exported_at': datetime.utcnow(), 'profile': profile, 'records': tables}),
                        headers={'Cache-Control': 'no-store', 'Content-Disposition': 'attachment; filename="root404-export.json"'})


@router.delete('', dependencies=[Depends(auth_rate_limit), Depends(recent_auth)])
def delete_account(payload: DeleteConfirmation, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.confirmation != user.email:
        raise HTTPException(400, 'Confirm with your account email')
    from app.models.auth_state import OTPChallenge
    # Remove all audit rows concerning the user rather than leaving identity in
    # JSON/resource fields after a SET NULL. Backups follow operator retention.
    audit = Base.metadata.tables['audit_logs']
    db.execute(audit.delete().where((audit.c.user_id == user.id) | (audit.c.resource_id == user.id)))
    db.query(OTPChallenge).filter_by(email=user.email).delete()
    import hashlib
    from app.models.auth_state import AuthThrottle
    db.query(AuthThrottle).filter_by(key=hashlib.sha256(user.email.lower().encode()).hexdigest()).delete()
    # FK CASCADE removes owned code/messages/progress; SET NULL anonymizes shared
    # references (room host, opponent, corrector, booking) in the same transaction.
    db.execute(User.__table__.delete().where(User.id == user.id))
    db.commit()
    return JSONResponse({'ok': True, 'detail': 'Account and owned active-database records deleted'},
                        headers={'Cache-Control': 'no-store'})


@router.put('/profile', dependencies=[Depends(auth_rate_limit)])
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.display_name.strip():
        raise HTTPException(422, 'Display name cannot be empty')
    user.display_name = payload.display_name.strip()
    user.bio = payload.bio.strip()
    db.commit()
    return user.to_dict()
