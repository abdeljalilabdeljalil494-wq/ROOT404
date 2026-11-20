from datetime import datetime
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User
from test_rc_workflows import account, client


def test_notification_owner_scoping_pagination_idempotent_read_and_export():
    owner, headers = account()
    other, outsider = account()
    with SessionLocal() as db:
        rows = [Notification(user_id=owner, kind='test', text='Private message', path='/peer-review'),
                Notification(user_id=other, kind='test', text='Other private message', path='/dashboard')]
        db.add_all(rows); db.commit()
        first, second = (row.id for row in rows)
    assert client.get('/api/notifications').status_code == 401
    response = client.get('/api/notifications?limit=1', headers=headers)
    assert response.headers['cache-control'] == 'no-store'
    assert response.json()['unread_count'] == 1
    assert [row['id'] for row in response.json()['items']] == [first]
    assert client.get('/api/notifications?limit=101', headers=headers).status_code == 422
    assert client.get('/api/notifications?offset=-1', headers=headers).status_code == 422
    assert client.post('/api/notifications/'+second+'/read', headers=headers).status_code == 404
    initial = client.post('/api/notifications/'+first+'/read', headers=headers).json()['read_at']
    assert initial
    assert client.post('/api/notifications/'+first+'/read', headers=headers).json()['read_at'] == initial
    assert client.post('/api/notifications/read-all', headers=headers).json()['updated'] == 0
    assert client.get('/api/notifications', headers=outsider).json()['unread_count'] == 1
    exported = client.get('/api/account/export', headers=headers).json()['records']['notifications']
    assert [row['id'] for row in exported] == [first]
    with SessionLocal() as db:
        email = db.get(User, owner).email
    assert client.request('DELETE', '/api/account', headers=headers, json={'confirmation': email}).status_code == 200
    with SessionLocal() as db:
        assert db.get(Notification, first) is None
        assert db.get(Notification, second) is not None


def test_notification_bulk_mark_is_owner_scoped():
    owner, headers = account()
    other, outsider = account()
    with SessionLocal() as db:
        db.add_all([Notification(user_id=uid, kind='test', text='Text', path='/dashboard') for uid in [owner, owner, other]])
        db.commit()
    assert client.post('/api/notifications/read-all', headers=headers).json()['updated'] == 2
    assert client.get('/api/notifications', headers=headers).json()['unread_count'] == 0
    assert client.get('/api/notifications', headers=outsider).json()['unread_count'] == 1


def test_notification_retention_is_explicit_and_dry_run_preserves_data():
    from datetime import timedelta
    from app.services.retention import purge_expired
    owner, _ = account()
    with SessionLocal() as db:
        row = Notification(user_id=owner, kind='test', text='Old alert', path='/dashboard', created_at=datetime.utcnow()-timedelta(days=400))
        db.add(row); db.commit(); key=row.id
        assert purge_expired(db)['notifications'] >= 1
        assert db.get(Notification,key) is not None
        purge_expired(db,apply=True)
        db.expire_all()
        assert db.get(Notification,key) is None
