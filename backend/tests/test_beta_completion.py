"""Trusted record/API tests; successful submission fixtures are NOT judge evidence."""
from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor
import pytest
from app.core.database import SessionLocal
from app.models import MissionClaim,ModerationReport
from app.models.user import User
from app.models.project import Project,UserProjectProgress
from app.models.submission import Submission
from app.models.correction import Correction
from app.models.room import RoomMessage
from app.services.project_suites import seed_execution_projects
from test_rc_workflows import account,client


def successful(uid,days=0,status='success',score=100):
    with SessionLocal() as db:
        seed_execution_projects(db)
        project=db.query(Project).filter_by(slug='foundations-sum-python').one()
        row=Submission(user_id=uid,project_id=project.id,status=status,score=score,files={'main.py':'print(0)'},
                       created_at=datetime.utcnow()-timedelta(days=days))
        db.add(row);db.commit();return row.id


def test_mission_uses_owned_today_success_not_client_rewards_and_awards_once():
    uid,headers=account();other,outsider=account()
    successful(other);successful(uid,days=1);successful(uid,status='failed',score=0)
    assert client.get('/api/progress').status_code==401
    assert client.post('/api/progress/mission/claim',headers=headers,json={'score':100,'xp':999999,'user_id':other}).status_code==409
    sid=successful(uid)
    assert client.get('/api/progress',headers=headers).json()['mission']['status']=='ready'
    response=client.post('/api/progress/mission/claim',headers=headers,json={'xp':999999,'user_id':other})
    assert response.json()['xp_earned']==25
    assert client.post('/api/progress/mission/claim',headers=headers).status_code==409
    with SessionLocal() as db:
        assert db.get(User,uid).xp==25 and db.get(User,other).xp==0
        assert db.query(MissionClaim).filter_by(user_id=uid).one().submission_id==sid
    assert client.get('/api/progress',headers=outsider).json()['mission']['status']=='ready'


def test_parallel_claim_has_one_winner():
    uid,headers=account();successful(uid)
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses=list(pool.map(lambda _:client.post('/api/progress/mission/claim',headers=headers).status_code,range(2)))
    assert sorted(statuses)==[200,409]
    with SessionLocal() as db: assert db.get(User,uid).xp==25


def test_badges_reputation_distinct_peers_repeat_reads_no_xp():
    uid,headers=account();author,_=account();sid=successful(author)
    with SessionLocal() as db:
        project=db.query(Project).filter_by(slug='foundations-sum-python').one()
        db.add(UserProjectProgress(user_id=uid,project_id=project.id,status='passed'))
        for _ in range(4): db.add(Correction(submission_id=sid,author_id=author,corrector_id=uid,status='completed',score=100))
        db.add(Correction(submission_id=sid,author_id=uid,corrector_id=uid,status='completed',score=100))
        db.commit()
    first=client.get('/api/progress',headers=headers).json()['achievements']
    assert first['reputation']==54 and first['basis']['distinct_reviewed_authors']==1
    assert next(b for b in first['badges'] if b['id']=='first-project')['earned'] is True
    assert next(b for b in first['badges'] if b['id']=='peer-guide')['earned'] is False
    assert client.get('/api/progress',headers=headers).json()['achievements']==first
    assert client.get('/api/analytics/reputation',headers=headers).json()[0]['value']==54
    portfolio=client.get('/api/portfolio/me/portfolio',headers=headers).json()
    assert portfolio['reputation']==54 and any(b['name']=='Premier projet' for b in portfolio['badges'])
    with SessionLocal() as db: assert db.get(User,uid).xp==0


def test_reports_membership_privacy_admin_only_atomic_resolution_and_penalty():
    author,ah=account();reporter,rh=account();outsider,oh=account();admin,mh=account()
    with SessionLocal() as db: db.get(User,admin).is_admin=True;db.commit()
    room=client.post('/api/rooms/',headers=ah,json={'name':'Moderation test'}).json()['id']
    assert client.post(f'/api/rooms/{room}/join',headers=rh).status_code==200
    msg=client.post(f'/api/rooms/{room}/messages',headers=ah,json={'content':'Bad content'}).json()['id']
    payload={'message_id':msg,'reason':'Please review this message'}
    assert client.post('/api/moderation/reports',headers=oh,json=payload).status_code==404
    assert client.post('/api/moderation/reports',headers=ah,json=payload).status_code==400
    result=client.post('/api/moderation/reports',headers=rh,json=payload)
    assert result.status_code==200;rid=result.json()['id']
    assert client.post('/api/moderation/reports',headers=rh,json=payload).status_code==409
    assert client.get('/api/moderation/reports',headers=oh).json()==[]
    assert len(client.get('/api/moderation/reports',headers=rh).json())==1
    assert 'message' not in client.get('/api/moderation/reports',headers=rh).json()[0]
    assert client.post(f'/api/moderation/reports/{rid}/resolve',headers=rh,json={'action':'remove'}).status_code==403
    assert client.post(f'/api/moderation/reports/{rid}/resolve',headers=mh,json={'action':'remove'}).status_code==200
    assert client.post(f'/api/moderation/reports/{rid}/resolve',headers=mh,json={'action':'dismiss'}).status_code==409
    assert client.get(f'/api/rooms/{room}/messages',headers=rh).json()==[]
    assert client.get(f'/api/rooms/{room}',headers=rh).json()['messages']==[]
    assert client.get('/api/progress',headers=ah).json()['achievements']['reputation']==45
    export=client.get('/api/account/export',headers=rh).json()['records']
    assert len(export['moderation_reports'])==1
    assert 'reviewer_id' not in export['moderation_reports'][0]


def test_report_whitespace_and_nonexistent_targets_rejected():
    _,headers=account()
    assert client.post('/api/moderation/reports',headers=headers,json={'message_id':'none','reason':'      '}).status_code==422
    assert client.post('/api/moderation/reports',headers=headers,json={'message_id':'none','reason':'reason','status':'removed'}).status_code==422
    assert client.post('/api/moderation/reports',headers=headers,json={'message_id':'none','reason':'reason'}).status_code==404


def test_conflicted_administrator_cannot_resolve_report_and_dismissal_no_penalty():
    author,ah=account();reporter,rh=account();admin,mh=account()
    room=client.post('/api/rooms/',headers=ah,json={'name':'Conflict test'}).json()['id']
    client.post(f'/api/rooms/{room}/join',headers=rh)
    msg=client.post(f'/api/rooms/{room}/messages',headers=ah,json={'content':'Reviewed content'}).json()['id']
    rid=client.post('/api/moderation/reports',headers=rh,json={'message_id':msg,'reason':'Review requested'}).json()['id']
    with SessionLocal() as db:
        for uid in [author,reporter,admin]: db.get(User,uid).is_admin=True
        db.commit()
    for headers in [ah,rh]:
        assert client.post(f'/api/moderation/reports/{rid}/resolve',headers=headers,json={'action':'remove'}).status_code==403
    assert client.post(f'/api/moderation/reports/{rid}/resolve',headers=mh,json={'action':'dismiss'}).status_code==200
    assert len(client.get(f'/api/rooms/{room}/messages',headers=rh).json())==1
    assert client.get('/api/progress',headers=ah).json()['achievements']['reputation']==50
    assert client.get('/api/moderation/reports',headers=mh).json()[0]['message']=='Reviewed content'


def test_admin_provisioning_requires_host_consent_existing_verified_user_and_revokes_sessions(monkeypatch):
    from app.manage import set_admin
    uid,headers=account()
    with SessionLocal() as db:
        user=db.get(User,uid);email=user.email
        with pytest.raises(ValueError): set_admin(db,email,'grant')
        monkeypatch.setenv('ROOT404_ALLOW_ADMIN_CHANGE','yes')
        with pytest.raises(ValueError): set_admin(db,'missing@example.com','grant')
        set_admin(db,email,'grant')
        assert db.get(User,uid).is_admin is True
    assert client.get('/api/auth/me',headers=headers).status_code==401


def test_reporter_deletion_does_not_restore_removed_content_or_erase_sanction():
    author,ah=account();reporter,rh=account();admin,mh=account()
    with SessionLocal() as db:
        db.get(User,admin).is_admin=True;email=db.get(User,reporter).email;db.commit()
    room=client.post('/api/rooms/',headers=ah,json={'name':'Removal permanence'}).json()['id']
    client.post(f'/api/rooms/{room}/join',headers=rh)
    msg=client.post(f'/api/rooms/{room}/messages',headers=ah,json={'content':'Removed content'}).json()['id']
    rid=client.post('/api/moderation/reports',headers=rh,json={'message_id':msg,'reason':'Review this please'}).json()['id']
    assert client.post(f'/api/moderation/reports/{rid}/resolve',headers=mh,json={'action':'remove'}).status_code==200
    assert client.request('DELETE','/api/account',headers=rh,json={'confirmation':email}).status_code==200
    assert client.get(f'/api/rooms/{room}/messages',headers=ah).json()==[]
    assert client.get('/api/progress',headers=ah).json()['achievements']['reputation']==45
    with SessionLocal() as db:
        assert db.query(ModerationReport).filter_by(id=rid).first() is None
        assert db.get(RoomMessage,msg).removed_at is not None
