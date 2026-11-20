from datetime import datetime,timedelta
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.submission import Submission
from app.models.room import RoomMessage
from app.models.correction import CorrectionSlot,Correction
from app.core.security import create_access_token
client=TestClient(app)


def account():
    name='rc_'+uuid.uuid4().hex[:12]
    with SessionLocal() as db:
        user=User(username=name,email=name+'@example.com',display_name=name,is_verified=True)
        db.add(user);db.commit()
        return user.id,{'Authorization':'Bearer '+create_access_token({'sub':user.id})}


def test_room_full_rejoin_is_idempotent_and_messages_are_recent_not_first_page():
    uid,headers=account()
    _,other=account()
    room=client.post('/api/rooms/',headers=headers,json={'name':'RCroom','capacity':1}).json()
    assert client.post('/api/rooms/'+room['id']+'/join',headers=headers).status_code==200
    assert client.post('/api/rooms/'+room['id']+'/join',headers=other).status_code==409
    assert client.get('/api/rooms/'+room['id']+'/messages',headers=other).status_code==403
    with SessionLocal() as db:
        for i in range(105):
            db.add(RoomMessage(room_id=room['id'],user_id=uid,content=str(i),created_at=datetime.utcnow()+timedelta(seconds=i)))
        db.commit()
    messages=client.get('/api/rooms/'+room['id']+'/messages?limit=2',headers=headers).json()
    assert [m['text'] for m in messages]==['103','104']
    assert client.post('/api/rooms/',headers=headers,json={'name':'  '}).status_code==422


def test_review_booking_without_submission_never_consumes_slot_and_valid_booking_creates_correction():
    corrector_id,corrector=account()
    author_id,author=account()
    with SessionLocal() as db:
        project=db.query(Project).first()
        project_id=project.id
    start=datetime.utcnow()+timedelta(days=1)
    payload={'start_time':start.isoformat(),'end_time':(start+timedelta(minutes=30)).isoformat(),'project_id':project_id}
    response=client.post('/api/peer-review/slots',headers=corrector,json=payload)
    assert response.status_code==200,response.text
    slot=response.json()['id']
    assert client.post('/api/peer-review/slots/'+slot+'/book',headers=author).status_code==409
    with SessionLocal() as db:
        from app.models.notification import Notification
        assert db.query(Notification).filter(Notification.user_id.in_([author_id,corrector_id])).count() == 0
        assert not db.get(CorrectionSlot,slot).is_booked
        sub=Submission(user_id=author_id,project_id=project_id,files={'main.c':'int main(void){return 0;}'},status='failed',score=0)
        db.add(sub);db.commit()
    booked=client.post('/api/peer-review/slots/'+slot+'/book',headers=author)
    assert booked.status_code==200,booked.text
    with SessionLocal() as db:
        correction=db.get(Correction,booked.json()['correction_id'])
        assert correction.author_id==author_id and correction.corrector_id==corrector_id
        from app.models.notification import Notification
        assert db.query(Notification).filter(Notification.user_id.in_([author_id,corrector_id])).count() == 2
    assert client.post('/api/peer-review/slots/'+slot+'/book',headers=author).status_code in [400,409]
    bad={**payload,'end_time':start.isoformat()}
    assert client.post('/api/peer-review/slots',headers=corrector,json=bad).status_code==422
