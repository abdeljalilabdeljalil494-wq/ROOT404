"""Fixed-provider authorization code exchange. No dynamic issuer/redirect URLs."""
import base64
import hashlib
import secrets
from urllib.parse import urlencode, urlsplit
import httpx
import jwt
from fastapi import HTTPException
from app.core.config import settings

PROVIDERS={
    'google':('https://accounts.google.com/o/oauth2/v2/auth','https://oauth2.googleapis.com/token','openid email profile'),
    'github':('https://github.com/login/oauth/authorize','https://github.com/login/oauth/access_token','read:user user:email'),
}


def digest(value): return hashlib.sha256(value.encode()).hexdigest()


def configuration(provider):
    if provider not in PROVIDERS: raise HTTPException(404,'Unknown OAuth provider')
    values=[getattr(settings,provider.upper()+'_'+suffix) for suffix in ('CLIENT_ID','CLIENT_SECRET','REDIRECT_URI')]
    if not all(values): raise HTTPException(503,'OAuth provider not configured')
    uri=urlsplit(values[2])
    local=settings.ENVIRONMENT!='production' and uri.hostname in {'localhost','127.0.0.1'}
    if (uri.scheme!='https' and not (local and uri.scheme=='http')) or uri.username or uri.password or uri.query or uri.fragment or uri.path!=f'/oauth/callback/{provider}':
        raise HTTPException(503,'Invalid OAuth callback configuration')
    return values


def authorization(provider,state,verifier,nonce):
    client_id,_,redirect=configuration(provider)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    return PROVIDERS[provider][0]+'?'+urlencode(dict(client_id=client_id,redirect_uri=redirect,
        scope=PROVIDERS[provider][2],response_type='code',state=state,nonce=nonce,
        code_challenge=challenge,code_challenge_method='S256'))


async def identity(provider,code,verifier,nonce):
    client_id,secret,redirect=configuration(provider)
    # No redirect following or proxy environment; every URL is a fixed provider URL.
    async with httpx.AsyncClient(timeout=15,trust_env=False,follow_redirects=False) as client:
        async def request(method,url,**kwargs):
            async with client.stream(method,url,**kwargs) as response:
                response.raise_for_status()
                body=bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body)>262144: raise ValueError('Provider response too large')
                import json
                return json.loads(body)
        token=await request('POST',PROVIDERS[provider][1],data=dict(client_id=client_id,client_secret=secret,
            redirect_uri=redirect,code=code,code_verifier=verifier,grant_type='authorization_code'),
            headers={'Accept':'application/json'})
        if token.get('error') or not isinstance(token.get('access_token'),str): raise ValueError('Exchange rejected')
        if provider=='google':
            raw=token.get('id_token',''); header=jwt.get_unverified_header(raw)
            if header.get('alg')!='RS256': raise ValueError('Invalid algorithm')
            keys=await request('GET','https://www.googleapis.com/oauth2/v3/certs')
            matches=[key for key in keys['keys'] if key.get('kid')==header.get('kid') and key.get('kty')=='RSA']
            if len(matches)!=1: raise ValueError('Unknown signing key')
            key=jwt.PyJWK.from_dict(matches[0],algorithm='RS256').key
            claims=jwt.decode(raw,key,algorithms=['RS256'],audience=client_id,
                              options={'require':['iss','sub','aud','exp','iat','nonce','email','email_verified']})
            if claims['iss'] not in {'https://accounts.google.com','accounts.google.com'}: raise ValueError('Issuer mismatch')
            if isinstance(claims['aud'],list) and len(claims['aud'])>1 and 'azp' not in claims: raise ValueError('Authorized party required')
            if claims.get('azp',client_id)!=client_id: raise ValueError('Authorized party mismatch')
            if not secrets.compare_digest(claims['nonce'],nonce) or claims['email_verified'] is not True: raise ValueError('Unverified identity')
            if 'at_hash' in claims:
                expected=base64.urlsafe_b64encode(hashlib.sha256(token['access_token'].encode()).digest()[:16]).rstrip(b'=').decode()
                if not secrets.compare_digest(claims['at_hash'],expected): raise ValueError('Access token hash mismatch')
            subject,email=claims['sub'],claims['email']
        else:
            headers={'Authorization':'Bearer '+token['access_token'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
            profile=await request('GET','https://api.github.com/user',headers=headers)
            emails=await request('GET','https://api.github.com/user/emails',headers=headers)
            verified=[row['email'] for row in emails if row.get('primary') is True and row.get('verified') is True]
            if len(verified)!=1 or type(profile.get('id')) is not int or profile['id']<=0: raise ValueError('Verified email required')
            subject,email=str(profile['id']),verified[0]
        from email_validator import validate_email
        email=validate_email(email,check_deliverability=False).normalized.lower()
        if not isinstance(subject,str) or not 1<=len(subject)<=255: raise ValueError('Invalid subject')
        return subject,email
