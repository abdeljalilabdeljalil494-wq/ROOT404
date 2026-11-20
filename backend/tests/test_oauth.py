"""OAuth contract tests with provider doubles, not real app verification."""
import secrets
from urllib.parse import parse_qs,urlsplit
from datetime import datetime,timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import auth_rate_limit
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.oauth import OAuthIdentity,OAuthAttempt
from app.services import oauth
from test_rc_workflows import account


@pytest.fixture
def flow(monkeypatch):
    for provider in ('GOOGLE','GITHUB'):
        monkeypatch.setattr(settings,provider+'_CLIENT_ID','client-test')
        monkeypatch.setattr(settings,provider+'_CLIENT_SECRET','secret-test')
        monkeypatch.setattr(settings,provider+'_REDIRECT_URI','https://beta.example/oauth/callback/'+provider.lower())
    app.dependency_overrides[auth_rate_limit]=lambda:None
    with TestClient(app) as client: yield client
    app.dependency_overrides.pop(auth_rate_limit,None)


def begin(client,provider='google',headers=None):
    response=client.post(f'/api/auth/oauth/{provider}/link',headers=headers) if headers else client.get(f'/api/auth/oauth/{provider}/start')
    assert response.status_code==200,response.text
    query=parse_qs(urlsplit(response.json()['url']).query)
    assert query['code_challenge_method']==['S256'] and len(query['code_challenge'][0])==43
    assert 'HttpOnly' in response.headers['set-cookie'] and 'SameSite=lax' in response.headers['set-cookie']
    return {'state':query['state'][0],'code':'provider-code'}


@pytest.mark.parametrize('provider',['google','github'])
def test_success_duplicate_identity_and_replay(flow,monkeypatch,provider):
    subject=secrets.token_hex(10); email=subject+'@example.com'
    async def exchange(*args): return subject,email
    monkeypatch.setattr(oauth,'identity',exchange)
    payload=begin(flow,provider)
    response=flow.post(f'/api/auth/oauth/{provider}/complete',json=payload)
    assert response.status_code==200,response.text
    headers={'Authorization':'Bearer '+response.json()['access_token']}
    assert flow.get('/api/auth/me',headers=headers).json()['email']==email
    assert flow.post(f'/api/auth/oauth/{provider}/complete',json=payload).status_code==400
    again=flow.post(f'/api/auth/oauth/{provider}/complete',json=begin(flow,provider))
    assert again.status_code==200
    with SessionLocal() as db:
        assert db.query(OAuthIdentity).filter_by(provider=provider,subject=subject).count()==1


def test_state_csrf_provider_expiry_and_callback_errors(flow,monkeypatch):
    async def forbidden(*args): pytest.fail('Invalid state reached provider')
    monkeypatch.setattr(oauth,'identity',forbidden)
    payload=begin(flow)
    with TestClient(app) as outsider:
        assert outsider.post('/api/auth/oauth/google/complete',json=payload).status_code==400
    assert flow.post('/api/auth/oauth/github/complete',json=payload).status_code==400
    assert flow.post('/api/auth/oauth/google/complete',json={**payload,'error':'access_denied'}).status_code==400
    payload=begin(flow)
    with SessionLocal() as db:
        db.query(OAuthAttempt).filter_by(state_hash=oauth.digest(payload['state'])).update({'expires_at':datetime.utcnow()-timedelta(seconds=1)})
        db.commit()
    assert flow.post('/api/auth/oauth/google/complete',json=payload).status_code==400


def test_email_collision_requires_authenticated_explicit_link(flow,monkeypatch):
    uid,headers=account()
    from app.models.user import User
    with SessionLocal() as db: email=db.get(User,uid).email
    subject=secrets.token_hex(12)
    async def exchange(*args): return subject,email
    monkeypatch.setattr(oauth,'identity',exchange)
    assert flow.post('/api/auth/oauth/google/complete',json=begin(flow)).status_code==409
    payload=begin(flow,headers=headers)
    assert flow.post('/api/auth/oauth/google/complete',json=payload).status_code==403
    response=flow.post('/api/auth/oauth/google/complete',json=payload,headers=headers)
    assert response.status_code==200 and response.json()['linked'] is True
    other,outsider=account()
    payload=begin(flow,headers=outsider)
    assert flow.post('/api/auth/oauth/google/complete',json=payload,headers=outsider).status_code==409


def test_provider_failure_redaction_and_config_validation(flow,monkeypatch):
    async def failure(*args): raise ValueError('PRIVATE_SECRET')
    monkeypatch.setattr(oauth,'identity',failure)
    response=flow.post('/api/auth/oauth/google/complete',json=begin(flow))
    assert response.status_code==502 and 'PRIVATE_SECRET' not in response.text
    monkeypatch.setattr(settings,'GOOGLE_REDIRECT_URI','http://evil.example/oauth/callback/google')
    assert flow.get('/api/auth/oauth/google/start').status_code==503
    assert flow.get('/api/auth/oauth/unknown/start').status_code==404


@pytest.mark.parametrize('mutation',['valid','nonce','issuer','audience','expired','unverified','signature','multi_audience','azp','at_hash'])
def test_real_google_signature_and_claim_validation(flow,monkeypatch,mutation):
    import json,time,jwt,httpx,asyncio
    from cryptography.hazmat.primitives.asymmetric import rsa
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public=json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key())); public['kid']='key1'
    claims={'iss':'https://accounts.google.com','sub':'123','aud':'client-test','iat':int(time.time()),
            'exp':int(time.time())+120,'nonce':'nonce','email':'verified@example.com','email_verified':True}
    if mutation=='multi_audience': claims['aud']=['client-test','other-client']
    if mutation=='azp': claims['azp']='other-client'
    if mutation=='at_hash': claims['at_hash']='incorrect-hash'
    if mutation=='nonce': claims['nonce']='wrong'
    if mutation=='issuer': claims['iss']='https://evil.example'
    if mutation=='audience': claims['aud']='wrong-client'
    if mutation=='expired': claims['exp']=int(time.time())-10
    if mutation=='unverified': claims['email_verified']=False
    signing_key=rsa.generate_private_key(public_exponent=65537,key_size=2048) if mutation=='signature' else key
    token=jwt.encode(claims,signing_key,algorithm='RS256',headers={'kid':'key1'})
    real_client=httpx.AsyncClient
    def handler(request):
        if str(request.url)=='https://oauth2.googleapis.com/token':
            assert b'code_verifier=verifier' in request.content
            return httpx.Response(200,json={'access_token':'not-stored','id_token':token})
        assert str(request.url)=='https://www.googleapis.com/oauth2/v3/certs'
        return httpx.Response(200,json={'keys':[public]})
    monkeypatch.setattr(oauth.httpx,'AsyncClient',lambda **kwargs:real_client(transport=httpx.MockTransport(handler),**kwargs))
    if mutation=='valid': assert asyncio.run(oauth.identity('google','code','verifier','nonce'))==('123','verified@example.com')
    else:
        with pytest.raises(Exception): asyncio.run(oauth.identity('google','code','verifier','nonce'))


def test_github_requires_primary_verified_email(flow,monkeypatch):
    import asyncio,httpx
    real_client=httpx.AsyncClient
    def handler(request):
        if request.url.host=='github.com': return httpx.Response(200,json={'access_token':'test-access'})
        assert request.headers['authorization']=='Bearer test-access'
        return httpx.Response(200,json={'id':42} if request.url.path=='/user' else [{'email':'unsafe@example.com','primary':True,'verified':False}])
    monkeypatch.setattr(oauth.httpx,'AsyncClient',lambda **kwargs:real_client(transport=httpx.MockTransport(handler),**kwargs))
    with pytest.raises(ValueError,match='Verified'): asyncio.run(oauth.identity('github','code','verifier','nonce'))


def test_export_excludes_pkce_material_and_deletion_removes_identity(flow,monkeypatch):
    uid,headers=account()
    subject=secrets.token_hex(10)
    async def exchange(*args): return subject,'separate-verified@example.com'
    monkeypatch.setattr(oauth,'identity',exchange)
    payload=begin(flow,headers=headers)
    assert flow.post('/api/auth/oauth/google/complete',json=payload,headers=headers).status_code==200
    begin(flow,headers=headers)  # Leave a pending attempt to exercise deletion cascade.
    export=flow.get('/api/account/export',headers=headers)
    assert export.status_code==200
    assert len(export.json()['records']['oauth_identities'])==1
    assert 'verifier' not in export.text and 'nonce' not in export.text
    from app.models.user import User
    with SessionLocal() as db: email=db.get(User,uid).email
    response=flow.request('DELETE','/api/account',headers=headers,json={'confirmation':email})
    assert response.status_code==200
    with SessionLocal() as db:
        assert db.query(OAuthIdentity).filter_by(user_id=uid).count()==0
        assert db.query(OAuthAttempt).filter_by(user_id=uid).count()==0
