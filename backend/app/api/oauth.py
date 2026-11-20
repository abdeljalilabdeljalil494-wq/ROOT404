"""Browser-bound one-use OAuth, explicit linking; never auto-link by email."""
from datetime import datetime,timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, auth_rate_limit
from app.core.security import create_access_token
from app.core.config import settings
from app.api.account import recent_auth
from app.models.oauth import OAuthAttempt, OAuthIdentity
from app.models.user import User
from app.services import oauth

router=APIRouter(prefix='/auth/oauth',tags=['OAuth'])
COOKIE='root404_oauth_browser'


def start(provider,response,db,user=None):
    oauth.configuration(provider)
    state,browser,verifier,nonce=[secrets.token_urlsafe(48) for _ in range(4)]
    now=datetime.utcnow()
    db.query(OAuthAttempt).filter(OAuthAttempt.expires_at<now).delete()
    db.add(OAuthAttempt(state_hash=oauth.digest(state),browser_hash=oauth.digest(browser),provider=provider,
        verifier=verifier,nonce=nonce,user_id=user.id if user else None,
        session_version=user.session_version if user else None,expires_at=now+timedelta(minutes=5)))
    db.commit()
    response.set_cookie(COOKIE,browser,max_age=300,httponly=True,secure=settings.ENVIRONMENT=='production',samesite='lax',path='/api/auth/oauth')
    response.headers['Cache-Control']='no-store'
    return {'url':oauth.authorization(provider,state,verifier,nonce)}


@router.get('/{provider}/start',dependencies=[Depends(auth_rate_limit)])
def login_start(provider:str,response:Response,db:Session=Depends(get_db)):
    return start(provider,response,db)


@router.post('/{provider}/link',dependencies=[Depends(auth_rate_limit),Depends(recent_auth)])
def link_start(provider:str,response:Response,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return start(provider,response,db,user)


class Callback(BaseModel):
    state:str=Field(min_length=32,max_length=128)
    code:str=Field(default='',max_length=2048)
    error:str=Field(default='',max_length=100)


@router.post('/{provider}/complete',dependencies=[Depends(auth_rate_limit)])
async def complete(provider:str,payload:Callback,request:Request,response:Response,
                   user:User=Depends(get_current_user_optional),db:Session=Depends(get_db)):
    oauth.configuration(provider)
    browser=request.cookies.get(COOKIE,'')
    row=db.get(OAuthAttempt,oauth.digest(payload.state))
    if not row or row.provider!=provider or row.expires_at<datetime.utcnow() or not browser or not secrets.compare_digest(row.browser_hash,oauth.digest(browser)):
        raise HTTPException(400,'Invalid or expired OAuth state')
    if row.user_id and (not user or user.id!=row.user_id or user.session_version!=row.session_version):
        raise HTTPException(403,'Linking session changed; authenticate again')
    verifier,nonce,owner=row.verifier,row.nonce,row.user_id
    claimed=db.query(OAuthAttempt).filter_by(state_hash=row.state_hash).delete()
    db.commit()
    if claimed!=1: raise HTTPException(400,'OAuth state already used')
    response.delete_cookie(COOKIE,path='/api/auth/oauth')
    response.headers['Cache-Control']='no-store'
    if payload.error or not payload.code: raise HTTPException(400,'OAuth authorization declined or missing code')
    try:
        subject,email=await oauth.identity(provider,payload.code,verifier,nonce)
    except Exception:
        # Provider bodies/tokens/codes/secret exception details never enter logs.
        raise HTTPException(502,'OAuth identity verification failed') from None
    existing=db.query(OAuthIdentity).filter_by(provider=provider,subject=subject).first()
    if owner:
        if existing and existing.user_id!=owner: raise HTTPException(409,'Identity already linked')
        target=db.get(User,owner)
    elif existing:
        target=db.get(User,existing.user_id)
    else:
        if db.query(User).filter_by(email=email).first():
            raise HTTPException(409,'Sign in with email first, then explicitly link this provider in Settings')
        target=User(username='oauth_'+secrets.token_hex(8),email=email,display_name=email.split('@')[0][:50],is_verified=True)
        try:
            db.add(target); db.flush()
        except IntegrityError:
            db.rollback(); raise HTTPException(409,'Account already exists; sign in again') from None
    if not target or not target.is_active or not target.is_verified: raise HTTPException(403,'Account unavailable')
    try:
        if not existing:
            db.add(OAuthIdentity(provider=provider,subject=subject,user_id=target.id))
        db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409,'Account or provider already linked; sign in again') from None
    return {'access_token':create_access_token({'sub':target.id,'sv':target.session_version}),'token_type':'bearer','linked':bool(owner)}
