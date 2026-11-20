from datetime import datetime, timedelta
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.core.dependencies import _clear_rate_limiter
from app.models.user import User
from app.models.room import Room, RoomMember, RoomMessage
from app.models.mentor import MentorInteraction
from app.services.retention import purge_expired
client = TestClient(app)


def account():
    _clear_rate_limiter()
    name = 'privacy_' + uuid.uuid4().hex[:12]
    with SessionLocal() as db:
        user = User(username=name, email=name+'@example.com', display_name=name, is_verified=True)
        db.add(user); db.commit()
        return user.id, user.username, user.email, {'Authorization': 'Bearer '+create_access_token({'sub': user.id})}


def test_privacy_default_optin_owner_export_and_revoke_all():
    user_id, name, email, headers = account()
    other_id, _, other_email, other_headers = account()
    assert client.get('/api/account/privacy').status_code == 401
    assert client.get('/api/portfolio/'+name).status_code == 404
    assert client.get('/api/portfolio/'+name, headers=other_headers).status_code == 404
    assert client.get('/api/portfolio/me/portfolio', headers=headers).status_code == 200
    assert client.get('/api/account/privacy', headers=headers).json() == {'public_profile': False, 'directory_visible': False}
    assert client.put('/api/account/privacy', headers=headers, json={'public_profile': True, 'directory_visible': True}).status_code == 200
    assert client.get('/api/portfolio/'+name).status_code == 200
    export = client.get('/api/account/export', headers=headers)
    assert export.status_code == 200 and export.headers['cache-control'] == 'no-store'
    assert email in export.text and other_email not in export.text and 'hashed_password' not in export.text
    assert client.post('/api/account/sessions/revoke-all', headers=headers).status_code == 200
    assert client.get('/api/user/me', headers=headers).status_code == 401
    assert client.get('/api/user/me', headers=other_headers).status_code == 200


def test_confirmed_deletion_cascades_private_records_and_preserves_other_users():
    user_id, name, email, headers = account()
    other_id, _, _, other_headers = account()
    with SessionLocal() as db:
        room = Room(name='Shared', host_id=user_id)
        db.add(room); db.flush()
        room_id = room.id
        db.add_all([RoomMember(room_id=room_id, user_id=user_id), RoomMember(room_id=room_id, user_id=other_id),
                    RoomMessage(room_id=room_id, user_id=user_id, content='private message'),
                    MentorInteraction(user_id=user_id, kind='ask', message='private question', response={'text':'private advice'})])
        db.commit()
    assert client.request('DELETE', '/api/account', headers=headers, json={'confirmation':'wrong'}).status_code == 400
    response = client.request('DELETE', '/api/account', headers=headers, json={'confirmation':email})
    assert response.status_code == 200, response.text
    assert client.get('/api/user/me', headers=headers).status_code == 401
    with SessionLocal() as db:
        assert db.get(User, user_id) is None and db.get(User, other_id) is not None
        assert db.query(MentorInteraction).filter_by(user_id=user_id).count() == 0
        assert db.query(RoomMessage).filter_by(user_id=user_id).count() == 0
        assert db.get(Room, room_id).host_id is None
        assert db.query(RoomMember).filter_by(room_id=room_id, user_id=other_id).count() == 1


def test_retention_is_dry_run_until_explicitly_applied():
    user_id, _, _, _ = account()
    with SessionLocal() as db:
        old = MentorInteraction(user_id=user_id, kind='ask', message='old', response={}, created_at=datetime.utcnow()-timedelta(days=31))
        recent = MentorInteraction(user_id=user_id, kind='ask', message='recent', response={})
        db.add_all([old,recent]); db.commit()
        old_id, recent_id = old.id, recent.id
        assert purge_expired(db)['mentor_interactions'] >= 1
        assert db.get(MentorInteraction, old_id) is not None
        purge_expired(db, apply=True); db.expire_all()
        assert db.get(MentorInteraction, old_id) is None
        assert db.get(MentorInteraction, recent_id) is not None
