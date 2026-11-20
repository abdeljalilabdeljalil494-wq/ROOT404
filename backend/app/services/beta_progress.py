"""Beta policy v1: measured, trusted records only. No client scores/rewards."""
from datetime import datetime,timedelta
from sqlalchemy import func
from app.models import MissionClaim
from app.models.project import Project,UserProjectProgress
from app.models.submission import Submission
from app.models.correction import Correction
from app.models.room import RoomMessage
from app.services.gamification import GamificationService

REWARD=25


def mission(db,user):
    today=datetime.utcnow().date(); start=datetime.combine(today,datetime.min.time())
    # Uses the supplied executable Stream Sum specification, never originals.
    project=db.query(Project).filter_by(slug='foundations-sum-python').first()
    claim=db.query(MissionClaim).filter_by(user_id=user.id,day=today.isoformat()).first()
    evidence=None
    if project:
        evidence=db.query(Submission).filter(Submission.user_id==user.id,Submission.project_id==project.id,
            Submission.status=='success',Submission.score>=80,Submission.created_at>=start,
            Submission.created_at<start+timedelta(days=1)).order_by(Submission.created_at,Submission.id).first()
    return {'day':today.isoformat(),'title':'Valider Stream Sum — Python aujourd’hui (UTC)',
            'project_slug':project.slug if project else None,'reward_xp':REWARD,
            'status':'claimed' if claim else 'ready' if evidence else 'available' if project else 'unavailable',
            'submission_id':evidence.id if evidence else None,'policy':'beta-v1'}


def achievements(db,user):
    projects=db.query(UserProjectProgress).filter_by(user_id=user.id,status='passed').count()
    peers=db.query(func.count(func.distinct(Correction.author_id))).filter(
        Correction.corrector_id==user.id,Correction.author_id!=user.id,
        Correction.status=='completed',Correction.score.isnot(None)).scalar() or 0
    removed=db.query(func.count(RoomMessage.id)).filter(
        RoomMessage.user_id==user.id,RoomMessage.removed_at.isnot(None)).scalar() or 0
    streak=GamificationService.check_streak(user,db)['streak']
    definitions=[('first-project','Premier projet','bronze',projects>=1),
                 ('five-projects','Cinq projets','silver',projects>=5),
                 ('peer-guide','Guide de trois pairs','silver',peers>=3),
                 ('seven-days','Sept jours actifs UTC','gold',streak>=7)]
    return {'policy':'beta-v1','badges':[{'id':key,'name':name,'tier':tier,'earned':earned} for key,name,tier,earned in definitions],
            'reputation':max(0,min(100,50+min(30,projects*2)+min(20,peers*2)-min(50,removed*5))),
            'basis':{'passed_projects':projects,'distinct_reviewed_authors':peers,'removed_messages':removed},'streak':streak}
