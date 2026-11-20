from datetime import datetime, timedelta
import logging
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.core.dependencies import _clear_rate_limiter
from app.core.logging import SecretFilter
from app.core.security import create_access_token


def test_secret_redaction_includes_email_bearer_url_and_errors():
    record=logging.LogRecord('test',logging.WARNING,'',1,'Bearer abc.def.ghi user@example.com redis://u:password@host',(),None)
    SecretFilter().filter(record)
    assert 'abc.def.ghi' not in record.msg and 'user@example.com' not in record.msg and 'password' not in record.msg
    record=logging.LogRecord('test',logging.ERROR,'',1,'DB failed row: private source code',(),None)
    SecretFilter().filter(record)
    assert 'private source code' not in record.msg


def test_stale_session_cannot_delete_or_export_and_directory_optin_is_enforced():
    _clear_rate_limiter()
    name='secure_'+uuid.uuid4().hex[:10]
    with SessionLocal() as db:
        user=User(username=name,email=name+'@example.com',display_name=name,is_verified=True)
        db.add(user);db.commit()
        token=create_access_token({'sub':user.id, 'iat':datetime.utcnow()})
        # create_access_token overwrites issued-at, so construct a correctly signed
        # old but still unexpired token to check step-up policy separately.
        from app.core.config import settings
        import jwt
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM], options={'verify_aud':False})
        payload['iat']=int((datetime.utcnow()-timedelta(minutes=11)).timestamp())
        stale=jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
        headers={'Authorization':'Bearer '+token}
    client=TestClient(app)
    assert not any(item['user']==name for item in client.get('/api/leaderboard/').json())
    assert client.get('/api/account/export',headers={'Authorization':'Bearer '+stale}).status_code==403
    assert client.request('DELETE','/api/account',headers={'Authorization':'Bearer '+stale},json={'confirmation':name+'@example.com'}).status_code==403
    assert client.put('/api/account/privacy',headers=headers,json={'public_profile':False,'directory_visible':True}).status_code==200
    assert any(item['user']==name for item in client.get('/api/leaderboard/').json())
    response=client.put('/api/account/profile',headers=headers,json={'display_name':'Updated','bio':'Actual bio'})
    assert response.status_code==200 and response.json()['displayName']=='Updated'
