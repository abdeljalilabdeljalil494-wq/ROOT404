"""Explicit opt-in real deployment probes; never dump exception/credential text.

No schema changes. PostgreSQL must use verified TLS; Redis probe keys are scoped
and expired/deleted. SMTP acceptance is not recipient delivery: optional IMAP
receipt completes that check. A provider call needs explicit paid-call consent.
"""
import json
import os
from pathlib import Path
import secrets
import ssl
import sys
import uuid

results={}

def probe(name, required, operation):
    if not all(os.environ.get(key) for key in required):
        results[name]={'status':'BLOCKED','reason':'Required private configuration absent','required':required}
        return
    if os.environ.get('ROOT404_ALLOW_EXTERNAL_PROBES')!='yes':
        results[name]={'status':'BLOCKED','reason':'Explicit external probe opt-in required'}
        return
    try:
        operation()
        if name not in results:
            results[name]={'status':'VERIFIED','scope':'targeted live communication, not full production acceptance'}
    except Exception as error:
        results[name]={'status':'BLOCKED','reason':'Probe failed; details withheld','exception_type':type(error).__name__}


def postgres():
    import psycopg2
    from psycopg2.extensions import parse_dsn
    url=os.environ['ROOT404_VERIFY_DATABASE_URL']
    assert parse_dsn(url).get('sslmode')=='verify-full'
    with psycopg2.connect(url,connect_timeout=10) as connection,connection.cursor() as cursor:
        cursor.execute('SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid()')
        assert cursor.fetchone()[0]
        cursor.execute('SELECT version_num FROM alembic_version')
        assert cursor.fetchone()[0]=='0007'


def redis():
    from redis import Redis
    url=os.environ['ROOT404_VERIFY_REDIS_URL']
    assert url.startswith('rediss://')
    with Redis.from_url(url,ssl_cert_reqs='required',socket_timeout=10,socket_connect_timeout=10) as client:
        # Redis URL query options override keyword arguments. Pin the resolved
        # pool configuration before opening any connection, so a DSN cannot
        # silently turn certificate/hostname validation or deadlines off.
        client.connection_pool.connection_kwargs.update(ssl_cert_reqs='required',
            ssl_check_hostname=True,socket_timeout=10,socket_connect_timeout=10)
        assert client.ping()
        key='root404:rc-probe:'+uuid.uuid4().hex
        try:
            client.set(key,'probe',ex=30)
            assert client.get(key)==b'probe'
        finally:client.delete(key)


def smtp():
    import smtplib,imaplib,time
    from email.message import EmailMessage
    context=ssl.create_default_context(cafile=os.environ.get('ROOT404_VERIFY_CA_FILE'))
    token=uuid.uuid4().hex
    message=EmailMessage()
    message['From']=os.environ['ROOT404_VERIFY_SMTP_FROM']
    message['To']=os.environ['ROOT404_VERIFY_RECIPIENT']
    message['Subject']='ROOT404 RC probe '+token
    message.set_content('Opt-in delivery test, not a login code. Probe '+token)
    implicit=os.environ.get('ROOT404_VERIFY_SMTP_SSL')=='true'
    transport=smtplib.SMTP_SSL if implicit else smtplib.SMTP
    with transport(os.environ['ROOT404_VERIFY_SMTP_HOST'],int(os.environ.get('ROOT404_VERIFY_SMTP_PORT','465' if implicit else '587')),
                   timeout=15,**({'context':context} if implicit else {})) as client:
        if not implicit:client.starttls(context=context)
        if os.environ.get('ROOT404_VERIFY_SMTP_USERNAME'):
            client.login(os.environ['ROOT404_VERIFY_SMTP_USERNAME'],os.environ['ROOT404_VERIFY_SMTP_PASSWORD'])
        assert not client.send_message(message)
    keys=['ROOT404_VERIFY_IMAP_HOST','ROOT404_VERIFY_IMAP_USERNAME','ROOT404_VERIFY_IMAP_PASSWORD']
    if not all(os.environ.get(key) for key in keys):
        results['external_smtp']={'status':'IMPLEMENTED BUT UNVERIFIED','reason':'SMTP accepted message; recipient receipt NOT verified','required':keys}
        return
    with imaplib.IMAP4_SSL(os.environ[keys[0]],ssl_context=context,timeout=15) as mailbox:
        mailbox.login(os.environ[keys[1]],os.environ[keys[2]])
        mailbox.select('INBOX',readonly=True)
        for _ in range(10):
            status,data=mailbox.search(None,'SUBJECT','"ROOT404 RC probe '+token+'"')
            if status=='OK' and data[0]:return
            time.sleep(2)
        raise RuntimeError('Receipt absent')


def ai():
    import httpx
    assert os.environ.get('ROOT404_ALLOW_PAID_AI_PROBE')=='yes'
    with httpx.Client(trust_env=False,timeout=40,follow_redirects=False) as client:
        response=client.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},
            json={'model':os.environ.get('AI_MODEL','gpt-4o-mini'),'max_tokens':16,'messages':[{'role':'user','content':'Reply with the integer42 only.'}]})
        response.raise_for_status()
        assert response.json()['choices'][0]['message']['content'].strip()=='42'


def proxy():
    import httpx
    url=os.environ['ROOT404_VERIFY_PUBLIC_URL']
    assert url.startswith('https://')
    context=ssl.create_default_context(cafile=os.environ.get('ROOT404_VERIFY_CA_FILE'))
    with httpx.Client(trust_env=False,verify=context,timeout=15,follow_redirects=False) as client:
        root=client.get(url.rstrip('/')+'/')
        assert root.status_code==200 and '<html' in root.text.lower()
        response=client.get(url.rstrip('/')+'/api/health')
        assert response.status_code==200 and response.headers.get('x-content-type-options')=='nosniff'
        assert response.headers.get('strict-transport-security')


def main():
    results.clear()
    probe('postgresql_tls',['ROOT404_VERIFY_DATABASE_URL'],postgres)
    probe('redis_tls',['ROOT404_VERIFY_REDIS_URL'],redis)
    probe('external_smtp',['ROOT404_VERIFY_SMTP_HOST','ROOT404_VERIFY_SMTP_FROM','ROOT404_VERIFY_RECIPIENT'],smtp)
    probe('openai',['OPENAI_API_KEY'],ai)
    probe('nginx_tls',['ROOT404_VERIFY_PUBLIC_URL'],proxy)
    # SMTP operation can downgrade the optimistic probe result to accepted/unreceived.
    # Never let SMTP server acceptance become mailbox-delivery evidence.
    print(json.dumps(results,indent=2))
    return 0 if all(result["status"]=="VERIFIED" for result in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
