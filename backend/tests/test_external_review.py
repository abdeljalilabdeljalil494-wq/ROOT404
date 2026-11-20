"""Current external-review regressions; no real provider or sandbox claims."""
import logging
from pathlib import Path
import uuid
import pytest
from sqlalchemy import event
from app.core.config import Settings, settings, get_safe_database_url
from app.core.database import SessionLocal, engine
from app.core.logging import SecretFilter
from app.core.security import generate_and_store_otp, get_last_otp, _clear_stores
from app.core.dependencies import _clear_rate_limiter
from app.models.project import Project
from app.models.submission import Submission
from app.models.correction import Correction
from app.services.judge import validate_files
from test_rc_workflows import account, client


@pytest.mark.parametrize('endpoint', ['/api/auth/otp', '/api/auth/register'])
def test_dev_otp_requires_independent_optin(monkeypatch, endpoint):
    monkeypatch.setattr(settings, 'ENABLE_DEV_OTP', False, raising=False)
    _clear_stores(); _clear_rate_limiter()
    name='gate'+uuid.uuid4().hex[:10]
    payload={'email':name+'@example.com', 'username':name, 'display_name':'Gate'}
    response=client.post(endpoint,json=payload)
    assert response.status_code==200, response.text
    assert 'dev_otp' not in response.json()
    assert get_last_otp(payload['email']) is None


def test_dev_otp_default_false_and_production_rejects_optin(monkeypatch):
    monkeypatch.delenv("ENABLE_DEV_OTP", raising=False)
    assert Settings(_env_file=None).ENABLE_DEV_OTP is False
    with pytest.raises(ValueError, match='ENABLE_DEV_OTP'):
        Settings(_env_file=None, ENVIRONMENT='production', ENABLE_DEV_OTP=True,
                 SECRET_KEY='s'*64, EMAIL_PROVIDER='smtp', SMTP_HOST='smtp.example.com',
                 SMTP_FROM='sender@example.com', DATABASE_URL='postgresql://localhost/test')


@pytest.mark.parametrize('field',['GOOGLE_CLIENT_SECRET','GITHUB_CLIENT_SECRET'])
def test_oauth_secrets_are_redacted(monkeypatch,field):
    secret='synthetic-oauth-secret-'+field
    monkeypatch.setattr(settings,field,secret)
    record=logging.LogRecord('test',logging.WARNING,'',1,'credential='+secret,(),None)
    SecretFilter().filter(record)
    assert secret not in record.msg


def test_safe_database_log_has_no_query_or_credentials(monkeypatch):
    monkeypatch.setattr(settings,'DATABASE_URL','postgresql://user:syntheticpass@db/test?password=syntheticquery')
    safe=get_safe_database_url()
    assert 'syntheticpass' not in safe and 'syntheticquery' not in safe


@pytest.mark.parametrize('language', ['py','Python','js','JavaScript','c++','C'])
def test_regex_aliases_do_not_skip_defense_in_depth(language):
    code='system("id");' if language.lower() in ['c','c++'] else ('eval("1")' if language.lower() in ['js','javascript'] else 'import os')
    assert validate_files({'main.txt':code},language)[0] is False


def test_review_list_query_count_is_bounded_and_outsider_cannot_post():
    author_id,author=account(); reviewer_id,reviewer=account(); _,outsider=account()
    with SessionLocal() as db:
        project=db.query(Project).first()
        for _ in range(6):
            sub=Submission(user_id=author_id,project_id=project.id,files={'main.py':'print(0)'},status='failed')
            db.add(sub);db.flush()
            correction=Correction(author_id=author_id,corrector_id=reviewer_id,submission_id=sub.id,status='scheduled')
            db.add(correction);db.flush(); cid=correction.id
        db.commit()
    assert client.post('/api/peer-review/'+cid+'/review',headers=outsider,json={'score':100}).status_code==403
    queries=[]
    def count(conn,cursor,statement,parameters,context,executemany):
        if statement.lstrip().upper().startswith('SELECT'): queries.append(statement)
    event.listen(engine,'before_cursor_execute',count)
    try:
        response=client.get('/api/peer-review/',headers=reviewer)
    finally:
        event.remove(engine,'before_cursor_execute',count)
    assert response.status_code==200
    assert len(response.json()['as_corrector'])==6
    assert len(queries)<=6, f'{len(queries)} SELECTs for six corrections'


def test_application_capability_allowlists_are_minimal():
    import yaml
    root=Path(__file__).resolve().parents[2]
    services=yaml.safe_load((root/'docker-compose.yml').read_text())['services']
    assert services['backend'].get('cap_add',[])==[]
    assert set(services['frontend'].get('cap_add',[])) <= {'NET_BIND_SERVICE'}


def test_blackhole_refreshes_stale_activity_before_freezing():
    from datetime import datetime, timedelta
    from app.models.user import User
    from app.services.blackhole import BlackHoleService
    uid,_=account()
    with SessionLocal() as db:
        user=db.get(User,uid)
        user.last_activity=datetime.utcnow()-timedelta(days=500)
        db.commit()
    with SessionLocal() as stale, SessionLocal() as active:
        old=stale.get(User,uid)
        fresh=active.get(User,uid)
        fresh.last_activity=datetime.utcnow()
        active.commit()
        BlackHoleService.update_user_blackhole(old,stale)
    with SessionLocal() as db:
        assert db.get(User,uid).is_active is True
        assert db.get(User,uid).blackhole_days_left>0


def test_tracked_secret_guard_rejects_names_without_reading_blobs(tmp_path):
    import subprocess
    import sys
    root=Path(__file__).resolve().parents[2]
    script=root/'scripts/check_tracked_secrets.py'
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    private=tmp_path/'.env'
    private.write_text('SYNTHETIC_DO_NOT_PRINT=synthetic-only')
    subprocess.run(['git','-C',str(tmp_path),'add','.env'],check=True)
    result=subprocess.run([sys.executable,str(script)],cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode==1
    assert '.env' in result.stdout and 'SYNTHETIC_DO_NOT_PRINT' not in result.stdout
    subprocess.run(['git','-C',str(tmp_path),'rm','--cached','.env'],check=True,capture_output=True)
    (tmp_path/'.env.example').write_text('SECRET_KEY=')
    subprocess.run(['git','-C',str(tmp_path),'add','.env.example'],check=True)
    assert subprocess.run([sys.executable,str(script)],cwd=tmp_path,capture_output=True).returncode==0


def test_production_otp_uses_mail_not_dev_response(monkeypatch):
    from app.services import email
    from app.core.security import verify_otp
    uid,_=account()
    from app.models.user import User
    with SessionLocal() as db: address=db.get(User,uid).email
    mailbox=[]
    class SMTP:
        def __init__(self,*args,**kwargs): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def starttls(self,**kwargs): pass
        def send_message(self,message): mailbox.append(message.get_content())
    _clear_stores(); _clear_rate_limiter()
    monkeypatch.setattr(settings,'ENVIRONMENT','production')
    monkeypatch.setattr(settings,'ENABLE_DEV_OTP',False)
    monkeypatch.setattr(settings,'EMAIL_PROVIDER','smtp')
    monkeypatch.setattr(settings,'SMTP_HOST','mail.example.com')
    monkeypatch.setattr(settings,'SMTP_FROM','sender@example.com')
    monkeypatch.setattr(email.smtplib,'SMTP',SMTP)
    response=client.post('/api/auth/otp',json={'email':address})
    assert response.status_code==200 and 'dev_otp' not in response.json()
    assert len(mailbox)==1 and get_last_otp(address) is None
    import re
    code=re.search(r'code is (\d{6})',mailbox[0]).group(1)
    assert client.post('/api/auth/verify',json={'email':address,'code':'notcode'}).status_code in {400,422}
    assert client.post('/api/auth/verify',json={'email':address,'code':code}).status_code==200
    assert not verify_otp(address,code)


def test_trusted_proxy_chain_and_untrusted_xff():
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    api=FastAPI()
    @api.get('/')
    def address(request: Request): return {'ip':request.client.host}
    wrapped=ProxyHeadersMiddleware(api,trusted_hosts=['10.0.0.2'])
    with TestClient(wrapped,client=('203.0.113.5',1234)) as external:
        assert external.get('/',headers={'X-Forwarded-For':'1.2.3.4'}).json()['ip']=='203.0.113.5'
    with TestClient(wrapped,client=('10.0.0.2',1234)) as proxy:
        assert proxy.get('/',headers={'X-Forwarded-For':'1.2.3.4, 203.0.113.5'}).json()['ip']=='203.0.113.5'


def test_api_health_budget_and_exact_security_headers(monkeypatch):
    _clear_stores(); _clear_rate_limiter()
    monkeypatch.setattr(settings,'ENVIRONMENT','production')
    responses=[client.get('/api/health') for _ in range(61)]
    assert all(r.status_code==200 for r in responses[:60])
    assert responses[-1].status_code==429
    assert int(responses[-1].headers['Retry-After'])>0
    for response in [responses[0],responses[-1],client.get('/api/no-such-endpoint')]:
        assert response.headers['X-Content-Type-Options']=='nosniff'
        assert response.headers['X-Frame-Options']=='DENY'
        assert response.headers['Strict-Transport-Security']=='max-age=31536000; includeSubDomains'
        scripts=next(x for x in response.headers['Content-Security-Policy'].split(';') if x.strip().startswith('script-src'))
        assert scripts.strip()=="script-src 'self'"


def test_room_markup_roundtrips_as_plain_json_without_html_rewriting():
    _,headers=account()
    room=client.post('/api/rooms/',headers=headers,json={'name':'Plain text','capacity':2}).json()
    content='<img src=x onerror="alert(1)"><script>alert(1)</script>'
    response=client.post('/api/rooms/'+room['id']+'/messages',headers=headers,json={'content':content})
    assert response.status_code==200,response.text
    response=client.get('/api/rooms/'+room['id']+'/messages',headers=headers)
    assert response.headers['content-type'].startswith('application/json')
    assert response.json()[-1]['text']==content
