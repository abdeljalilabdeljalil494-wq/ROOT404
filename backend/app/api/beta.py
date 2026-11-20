from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,Request,Response,Query
from pydantic import BaseModel,Field,ConfigDict,field_validator
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user,require_admin,rate_limit
from app.models.user import User
from app.models import MissionClaim,ModerationReport
from app.models.room import RoomMessage,RoomMember
from app.services.beta_progress import mission,achievements,REWARD
from app.services.gamification import GamificationService

router=APIRouter(tags=['Beta progress and moderation'])


def mutation_limit(request:Request,user:User=Depends(get_current_user)):
    rate_limit(request,max_requests=30,window=60,key_prefix='beta-mutation:'+user.id)


@router.get('/progress')
def progress(response:Response,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    response.headers['Cache-Control']='no-store'
    return {'mission':mission(db,user),'achievements':achievements(db,user)}


@router.post('/progress/mission/claim',dependencies=[Depends(mutation_limit)])
def claim(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    # Same account lock as project XP on PostgreSQL; unique claim is final arbiter
    # on all databases. Insert/award commit or roll back together.
    user=db.query(User).filter_by(id=user.id).with_for_update().populate_existing().one()
    current=mission(db,user)
    if current['status']=='claimed': raise HTTPException(409,'Mission already claimed')
    if current['status']!='ready': raise HTTPException(409,'A successful owned submission today is required')
    try:
        db.add(MissionClaim(user_id=user.id,day=current['day'],submission_id=current['submission_id'],xp=REWARD))
        db.flush()
        GamificationService.add_xp(user,REWARD,'Daily mission beta-v1',db,commit=False)
        db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Mission already claimed') from None
    return {'xp_earned':REWARD,'day':current['day']}


class ReportInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    message_id:str=Field(min_length=1,max_length=32)
    reason:str=Field(min_length=5,max_length=1000)

    @field_validator('reason')
    @classmethod
    def nonblank(cls,value):
        if len(value.strip())<5: raise ValueError('Explain the report')
        return value.strip()


def public_report(row):
    return {'id':row.id,'message_id':row.message_id,'reason':row.reason,'status':row.status,
            'created_at':row.created_at.isoformat(),'resolved_at':row.resolved_at.isoformat() if row.resolved_at else None}


@router.post('/moderation/reports',dependencies=[Depends(mutation_limit)])
def report(payload:ReportInput,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    message=db.get(RoomMessage,payload.message_id)
    if not message or not db.query(RoomMember).filter_by(room_id=message.room_id,user_id=user.id).first():
        raise HTTPException(404,'Message not found')
    if message.user_id==user.id: raise HTTPException(400,'Cannot report your own message')
    if db.query(ModerationReport).filter_by(user_id=user.id,message_id=message.id).first():
        raise HTTPException(409,'Already reported')
    row=ModerationReport(user_id=user.id,message_id=message.id,reason=payload.reason)
    try:
        db.add(row);db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Already reported') from None
    return public_report(row)


@router.get('/moderation/reports')
def reports(response:Response,limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0,le=10000),
            user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    response.headers['Cache-Control']='no-store'
    query=db.query(ModerationReport)
    if not user.is_admin: query=query.filter_by(user_id=user.id)
    result=[]
    for row in query.order_by(ModerationReport.created_at.desc(),ModerationReport.id).offset(offset).limit(limit):
        item=public_report(row)
        if user.is_admin:
            message=db.get(RoomMessage,row.message_id)
            item['message']=message.content if message else None
            item['can_resolve']=bool(message and row.status=='open' and row.user_id!=user.id and message.user_id!=user.id)
        result.append(item)
    return result


class ResolveInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    action:str=Field(pattern='^(remove|dismiss)$')


@router.post('/moderation/reports/{report_id}/resolve',dependencies=[Depends(mutation_limit)])
def resolve(report_id:str,payload:ResolveInput,user:User=Depends(require_admin),db:Session=Depends(get_db)):
    row=db.get(ModerationReport,report_id)
    if not row: raise HTTPException(404,'Report not found')
    message=db.get(RoomMessage,row.message_id)
    if not message: raise HTTPException(404,'Message not found')
    if row.user_id==user.id or message.user_id==user.id:
        raise HTTPException(403,'Another administrator must review conflicts of interest')
    changed=db.execute(update(ModerationReport).where(ModerationReport.id==report_id,
        ModerationReport.status=='open').values(status='removed' if payload.action=='remove' else 'dismissed',
        reviewer_id=user.id,resolved_at=datetime.utcnow())).rowcount
    if changed!=1:
        db.rollback();raise HTTPException(409,'Report already resolved')
    if payload.action=='remove':
        db.execute(update(RoomMessage).where(RoomMessage.id==row.message_id,RoomMessage.removed_at.is_(None)).values(removed_at=datetime.utcnow()))
    db.commit()
    return {'ok':True}
