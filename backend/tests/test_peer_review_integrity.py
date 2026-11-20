from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models.user import User
from app.models.submission import Submission
from app.models.correction import Correction, CorrectionSlot
from app.models.notification import Notification
from app.models.project import Project
from test_rc_workflows import account, client


def test_review_authorization_finality_points_and_transactional_notification():
    reviewer_id, reviewer = account()
    author_id, author = account()
    _, outsider = account()
    with SessionLocal() as db:
        project = db.query(Project).first()
        sub = Submission(user_id=author_id, project_id=project.id, files={'main.py': 'print(0)'}, status='failed', score=0)
        db.add(sub); db.flush()
        correction = Correction(author_id=author_id, corrector_id=reviewer_id, submission_id=sub.id, status='scheduled')
        db.add(correction); db.commit()
        cid, sid = correction.id, sub.id
        before = db.get(User, reviewer_id).correction_points
    endpoint = '/api/peer-review/'+cid+'/review'
    assert client.get('/api/peer-review/'+cid, headers=outsider).status_code == 403
    assert client.post(endpoint, headers=author, json={'score': 100}).status_code == 403
    assert client.post(endpoint, headers=reviewer, json={'score': 101}).status_code == 422
    accepted = client.post(endpoint, headers=reviewer, json={'score': 90, 'comment': 'Human feedback'})
    assert accepted.status_code == 200, accepted.text
    assert client.post(endpoint, headers=reviewer, json={'score': 0}).status_code == 409
    with SessionLocal() as db:
        assert db.get(User, reviewer_id).correction_points == before + accepted.json()['correction_points_earned']
        assert db.get(Submission, sid).status == 'failed'  # human opinion is not judge evidence
        assert db.get(Correction, cid).score == 90
        assert db.scalar(select(func.count()).select_from(Notification).where(Notification.user_id==author_id)) == 1
    alerts = client.get('/api/notifications', headers=author).json()['items']
    assert alerts[0]['kind'] == 'review_completed'
