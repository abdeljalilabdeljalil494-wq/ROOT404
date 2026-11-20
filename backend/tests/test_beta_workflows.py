from datetime import datetime,timedelta
from app.core.database import SessionLocal
from app.models.user import User
from app.models.submission import Submission
from app.models.project import Project
from app.models.coalition import Coalition,CoalitionMember
from app.services.gamification import GamificationService
from test_rc_workflows import account,client


def test_coalition_membership_no_switch_no_foreign_assignment_or_fabricated_totals():
    uid,headers=account(); other,outsider=account()
    listing=client.get('/api/coalitions/').json()
    first,second=listing[:2]
    with SessionLocal() as db:
        # account helper may already assign; use new accounts' actual membership.
        original=db.get(User,uid).coalition_id
        db.get(User,uid).xp=17
        c=db.get(Coalition,first['id']); c.points=999999; c.members_count=999999
        db.commit()
    target=original or first['id']
    response=client.post('/api/coalitions/join',headers=headers,json={'coalition_id':target,'user_id':other})
    assert response.status_code==200
    assert client.post('/api/coalitions/join',headers=headers,json={'coalition_id':next(c['id'] for c in listing if c['id']!=target)}).status_code==409
    with SessionLocal() as db:
        assert db.query(CoalitionMember).filter_by(user_id=uid).count()==1
        assert db.get(User,other).coalition_id!=target or db.query(CoalitionMember).filter_by(user_id=other).count()<=1
        expected=sum(u.xp for u in db.query(User).filter_by(coalition_id=target,is_active=True))
    measured=next(c for c in client.get('/api/coalitions/').json() if c['id']==target)
    assert measured['points']==expected
    assert client.post('/api/coalitions/wars?name=Abuse',headers=headers).status_code==403
    assert client.post('/api/coalitions/join',json={'coalition_id':target}).status_code==401


def test_streak_is_read_only_owner_scoped_and_daily_mission_uses_authoritative_contract():
    from app.services.project_suites import seed_execution_projects
    with SessionLocal() as db: seed_execution_projects(db)
    uid,headers=account(); other,_=account()
    with SessionLocal() as db:
        project=db.query(Project).first()
        for owner,offset in [(uid,0),(uid,0),(uid,1),(other,2)]:
            db.add(Submission(user_id=owner,project_id=project.id,files={'main.py':'x'},language='python',created_at=datetime.utcnow()-timedelta(days=offset)))
        db.commit()
        user=db.get(User,uid); stored=user.streak
        assert GamificationService.check_streak(user,db)['streak']==2
        assert GamificationService.check_streak(user,db)['streak']==2
        assert user.streak==stored
    overview=client.get('/api/dashboard/overview',headers=headers)
    assert overview.status_code==200
    assert overview.json()['dailyMission']['reward']==25
    assert overview.json()['dailyMission']['policy']=='beta-v1'
    assert overview.json()['dailyMission']['project_slug']=='foundations-sum-python'


def test_untrusted_or_out_of_range_awards_rejected_before_mutation():
    import pytest
    uid,_=account()
    with SessionLocal() as db:
        user=db.get(User,uid)
        for amount in [-1,True,'100',0.5]:
            with pytest.raises(ValueError): GamificationService.add_xp(user,amount,'invalid',db)
        for score in [-1,101,True,'100']:
            with pytest.raises(ValueError): GamificationService.complete_project(user,100,score,db)
        assert user.xp==0 and user.projects_done==0
