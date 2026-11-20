"""Real local PostgreSQL/Redis/STARTTLS integration (NOT production verification).

Requires explicit disposable-DB admin DSN in ROOT404_PG_ADMIN_DSN, local Redis
credentials in ignored .cache/infrastructure/verify.json, and local_smtp_sink.py.
Never points the application tests at an existing user's database. Creates/drops
only its random temporary DB/role. Credentials/code/mail are never printed.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from email import policy
from email.parser import BytesParser
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import uuid
import psycopg2
from psycopg2 import sql
from redis import Redis

root = Path(__file__).resolve().parents[1]
os.chdir(root)
admin = psycopg2.connect(os.environ['ROOT404_PG_ADMIN_DSN'])
admin.autocommit = True
name = 'root404_verify_' + uuid.uuid4().hex[:12]
password = secrets.token_hex(32)
config = json.loads((root/'.cache/infrastructure/verify.json').read_text())
# This verifier intentionally connects over TCP with password authentication,
# not the local trusted admin socket used to provision the disposable database.
url = f'postgresql://{name}:{password}@127.0.0.1:55432/{name}'
env = dict(os.environ, DATABASE_URL=url, ENVIRONMENT='production', SECRET_KEY=secrets.token_hex(32),
           EMAIL_PROVIDER='smtp', SMTP_HOST='localhost', SMTP_PORT='5587', SMTP_FROM='noreply@root404.test',
           REDIS_URL=config['redis_url'], SSL_CERT_FILE=str(root/'.cache/infrastructure/smtp.pem'),
           SEED_DEMO_DATA='false', ENABLE_DEMO_FEATURES='false', ENABLE_DEV_OTP='false')
results = []

def passed(message):
    results.append(message)
    print('PASS: ' + message, flush=True)


def migration(*args):
    subprocess.run([sys.executable, '-m', 'alembic', '-c', 'backend/alembic.ini', *args],
                   env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

try:
    with admin.cursor() as cursor:
        cursor.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD %s').format(sql.Identifier(name)), (password,))
        cursor.execute(sql.SQL("CREATE DATABASE {} OWNER {} ENCODING 'UTF8' TEMPLATE template0 LC_COLLATE 'C' LC_CTYPE 'C'").format(sql.Identifier(name),sql.Identifier(name)))
    migration('upgrade','0001')
    with psycopg2.connect(url) as connection, connection.cursor() as cursor:
        cursor.execute("INSERT INTO badges (id,name,icon,tier,criteria) VALUES ('preserve','Preserve','Star','bronze','{}')")
    migration('upgrade','head')
    with psycopg2.connect(url) as connection, connection.cursor() as cursor:
        cursor.execute('SELECT version_num FROM alembic_version')
        assert cursor.fetchone()[0] == '0007'
        cursor.execute("SELECT name FROM badges WHERE id='preserve'")
        assert cursor.fetchone()[0] == 'Preserve'
    migration('downgrade','0001'); migration('upgrade','head')
    passed('PostgreSQL fresh baseline, existing-row upgrade0001->0007, downgrade/re-upgrade')
    # Real logical backup/restore into a SECOND disposable database.
    import pgserver
    tools = Path(pgserver.__file__).parent/'pginstall/bin'
    backup = root/'.cache/infrastructure/verification.dump'
    pg_env = dict(os.environ, PGPASSWORD=password)
    subprocess.run([str(tools/'pg_dump'), '-h','127.0.0.1','-p','55432','-U',name,
                    '-Fc','-f',str(backup),name], env=pg_env, check=True, stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    restore_name = name+'_restore'
    with admin.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE DATABASE {} OWNER {} ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(restore_name),sql.Identifier(name)))
    try:
        subprocess.run([str(tools/'pg_restore'), '-h','127.0.0.1','-p','55432','-U',name,
                        '-d',restore_name,str(backup)],env=pg_env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        with psycopg2.connect(url.rsplit('/',1)[0]+'/'+restore_name) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT name FROM badges WHERE id='preserve'")
            assert cursor.fetchone()[0]=='Preserve'
            cursor.execute('SELECT version_num FROM alembic_version')
            assert cursor.fetchone()[0]=='0007'
    finally:
        with admin.cursor() as cursor:
            cursor.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(restore_name)))
        backup.unlink(missing_ok=True)
    passed('PostgreSQL real pg_dump/pg_restore into second database preserves row and migration head')
    # Set env BEFORE importing app; backend/tests/conftest.py is never loaded here.
    os.environ.update(env)
    sys.path.insert(0, str(root/'backend'))
    from app.core.database import SessionLocal, engine
    from app.core.rate_limit import RateLimiter
    from app.core.security import store_otp, verify_otp, create_access_token
    from app.models.user import User
    from app.models.mentor import MentorInteraction
    from app.main import app
    from fastapi.testclient import TestClient
    from app.services.project_suites import seed_execution_projects
    assert engine.dialect.name == 'postgresql'
    limiter = RateLimiter()
    key = 'postgres-concurrency-'+uuid.uuid4().hex
    with ThreadPoolExecutor(8) as pool:
        answers = list(pool.map(lambda _: limiter.is_allowed(key,5,60)[0], range(32)))
    assert sum(answers) == 5
    passed('PostgreSQL atomic shared throttle accepts exactly5 of32 concurrent requests')
    recipient = name+'@example.com'
    store_otp(recipient,'135790')
    with ThreadPoolExecutor(8) as pool:
        answers = list(pool.map(lambda _: verify_otp(recipient,'135790'), range(16)))
    assert sum(answers) == 1
    passed('PostgreSQL concurrent OTP single consumption (1 of16)')
    with SessionLocal() as db:
        first = User(username='verify_owner', email=recipient, display_name='Owner', is_verified=True)
        other = User(username='verify_other', email='other@root404.test', display_name='Other', is_verified=True)
        db.add_all([first,other]); db.commit()
        owner_id, other_id = first.id, other.id
        token=create_access_token({'sub':owner_id})
        seed_execution_projects(db)
        db.add(MentorInteraction(user_id=owner_id,kind='ask',message='Owned',response={'role':'ai','text':'Stored'}));db.commit()
    headers={'Authorization':'Bearer '+token}
    with TestClient(app) as client:
        assert client.get('/ready').status_code == 200
        # End-to-end API OTP issuance -> actual STARTTLS mailbox -> verification.
        before_auth = set((root/'.cache/infrastructure/mail').glob('*.eml'))
        otp_response = client.post('/api/auth/login', json={'email':recipient})
        assert otp_response.status_code == 200 and 'dev_otp' not in otp_response.json()
        delivered_auth = set((root/'.cache/infrastructure/mail').glob('*.eml'))-before_auth
        assert len(delivered_auth) == 1
        auth_message = BytesParser(policy=policy.default).parsebytes(delivered_auth.pop().read_bytes())
        code = re.search(r'code is (\d{6})', auth_message.get_body().get_content()).group(1)
        verified = client.post('/api/auth/verify', json={'email':recipient,'code':code})
        assert verified.status_code == 200, verified.status_code
        assert client.post('/api/auth/verify', json={'email':recipient,'code':code}).status_code == 400
        passed('Production-config API OTP issuance -> actual STARTTLS mailbox -> verification/replay rejection')
        # Real capacity contention, not SQLite's no-op FOR UPDATE.
        from app.models.room import RoomMember
        room=client.post('/api/rooms/',headers=headers,json={'name':'Native capacity','capacity':2}).json()
        join_headers=[]
        with SessionLocal() as db:
            for index in range(6):
                learner=User(username='capacity_'+str(index),email='capacity'+str(index)+'@example.com',display_name='Capacity',is_verified=True)
                db.add(learner);db.flush()
                join_headers.append({'Authorization':'Bearer '+create_access_token({'sub':learner.id})})
            db.commit()
        with ThreadPoolExecutor(6) as pool:
            joined=list(pool.map(lambda hdr:client.post('/api/rooms/'+room['id']+'/join',headers=hdr),join_headers))
        assert sorted(r.status_code for r in joined)==[200,409,409,409,409,409]
        with SessionLocal() as db:
            assert db.query(RoomMember).filter_by(room_id=room['id']).count()==2
        passed('Real PostgreSQL six simultaneous joins for one remaining seat: one accepted, five409')
        # Real PG stale worker session must reread the activity committed elsewhere.
        from app.services.blackhole import BlackHoleService
        from datetime import datetime, timedelta
        with SessionLocal() as db:
            learner=db.get(User,other_id)
            learner.last_activity=datetime.utcnow()-timedelta(days=500)
            db.commit()
        with SessionLocal() as stale, SessionLocal() as active:
            old=stale.get(User,other_id)
            fresh=active.get(User,other_id)
            fresh.last_activity=datetime.utcnow()
            active.commit()
            BlackHoleService.update_user_blackhole(old,stale)
        with SessionLocal() as db:
            assert db.get(User,other_id).is_active and db.get(User,other_id).blackhole_days_left>0
        passed('Real PostgreSQL stale BlackHole worker refreshes committed activity before freeze')
        # No successful evaluation is fabricated: parallel disabled-judge requests
        # must create neither submissions nor XP. Reward success gate stays blocked.
        with SessionLocal() as db:
            before_xp=db.get(User,owner_id).xp
        with ThreadPoolExecutor(2) as pool:
            submitted=list(pool.map(lambda _:client.post('/api/projects/foundations-sum-python/submit',headers=headers,json={'files':{'main.py':'print(0)'},'language':'python'}),range(2)))
        assert all(r.status_code==503 for r in submitted)
        with SessionLocal() as db:
            from app.models.submission import Submission
            assert db.get(User,owner_id).xp==before_xp
            assert db.query(Submission).filter_by(user_id=owner_id).count()==0
        passed('Real PostgreSQL parallel disabled-judge submissions:503, no submissions or XP; NOT successful judge proof')
        # Real PG row-lock/CAS lifecycle. These failed submissions are fixtures,
        # not claimed judge execution. Exactly one author may consume a slot.
        from datetime import datetime, timedelta
        from app.models.submission import Submission
        from app.models.project import Project
        from app.models.notification import Notification
        with SessionLocal() as db:
            challenger = User(username='verify_challenger', email='challenger@example.com', display_name='Challenger', is_verified=True)
            db.add(challenger); db.flush()
            challenger_id=challenger.id
            project_id=db.query(Project).filter_by(slug='foundations-sum-python').one().id
            for uid in [owner_id,challenger_id]:
                db.add(Submission(user_id=uid,project_id=project_id,files={'main.py':'print(0)'},status='failed',score=0))
            db.commit()
        reviewer_headers={'Authorization':'Bearer '+create_access_token({'sub':other_id})}
        challenger_headers={'Authorization':'Bearer '+create_access_token({'sub':challenger_id})}
        start=datetime.utcnow()+timedelta(days=1)
        payload={'project_id':project_id,'start_time':start.isoformat(),'end_time':(start+timedelta(minutes=30)).isoformat()}
        # Concurrent overlapping slot publication must serialize per corrector.
        with ThreadPoolExecutor(2) as pool:
            published=list(pool.map(lambda _:client.post('/api/peer-review/slots',headers=reviewer_headers,json=payload),range(2)))
        assert sorted(response.status_code for response in published)==[200,409]
        slot_id=next(response.json()['id'] for response in published if response.status_code==200)
        with ThreadPoolExecutor(2) as pool:
            booked=list(pool.map(lambda hdr:client.post('/api/peer-review/slots/'+slot_id+'/book',headers=hdr),[headers,challenger_headers]))
        assert sum(response.status_code==200 for response in booked)==1
        assert all(response.status_code in [200,400,409] for response in booked)
        correction_id=next(response.json()['correction_id'] for response in booked if response.status_code==200)
        with ThreadPoolExecutor(2) as pool:
            reviewed=list(pool.map(lambda _:client.post('/api/peer-review/'+correction_id+'/review',headers=reviewer_headers,json={'score':85,'comment':'Native PostgreSQL review'}),range(2)))
        assert sorted(response.status_code for response in reviewed)==[200,409]
        assert client.get('/api/notifications',headers=reviewer_headers).json()['unread_count']==1
        with SessionLocal() as db:
            assert db.get(User,other_id).correction_points == 70
            assert db.query(Notification).count()==3  # two booking + one final review
        passed('Real PostgreSQL simultaneous slot overlap, single booking/review award and transactional private notifications')
        # Trusted DB fixture isolates reward concurrency from unavailable judge.
        from app.models.submission import Submission
        from app.models.project import Project
        from app.models import MissionClaim
        with SessionLocal() as db:
            project=db.query(Project).filter_by(slug='foundations-sum-python').one()
            db.add(Submission(user_id=owner_id,project_id=project.id,status='success',score=100,files={'main.py':'print(0)'}))
            db.commit(); before_xp=db.get(User,owner_id).xp
        with ThreadPoolExecutor(4) as pool:
            claimed=list(pool.map(lambda _:client.post('/api/progress/mission/claim',headers=headers),range(4)))
        assert sorted(response.status_code for response in claimed)==[200,409,409,409]
        with SessionLocal() as db:
            assert db.get(User,owner_id).xp==before_xp+25
            assert db.query(MissionClaim).filter_by(user_id=owner_id).count()==1
        passed('Real PostgreSQL parallel daily mission claims: one reward, trusted submission fixture NOT judge execution')
        assert client.get('/api/account/export',headers=headers).status_code == 200
        assert len(client.get('/api/ai/history',headers=headers).json()) == 2
        assert client.get('/api/portfolio/verify_owner').status_code == 404
        assert client.request('DELETE','/api/account',headers=headers,json={'confirmation':recipient}).status_code == 200
        assert client.get('/api/user/me',headers=headers).status_code == 401
    with SessionLocal() as db:
        assert db.get(User,owner_id) is None and db.get(User,other_id) is not None
        assert db.query(MentorInteraction).filter_by(user_id=owner_id).count() == 0
    passed('Real PostgreSQL API readiness, owner export/history, private portfolio and account deletion cascade')
    with Redis.from_url(config['redis_url']) as redis:
        assert redis.ping()
        key='root404:verification:'+uuid.uuid4().hex
        redis.set(key,'persisted',ex=600)
        with Redis.from_url(config['redis_url']) as other:
            assert other.get(key)==b'persisted'
        # AOF persistence is checked by a separate real restart in this run.
        (root/'.cache/infrastructure/redis-proof-key').write_text(key)
    from app.core.cache import check_redis_health
    assert check_redis_health() is True
    passed('Real Redis authenticated write/read from separate clients and application readiness')
    from app.services.email import send_otp
    before = set((root/'.cache/infrastructure/mail').glob('*.eml'))
    send_otp('delivery@root404.test','246810')
    delivered = set((root/'.cache/infrastructure/mail').glob('*.eml'))-before
    assert len(delivered)==1
    message=BytesParser(policy=policy.default).parsebytes(delivered.pop().read_bytes())
    assert message['To']=='delivery@root404.test' and '246810' in message.get_body().get_content()
    passed('Actual SMTP STARTTLS with verified local certificate and mailbox delivery (not Internet delivery)')
    (root/'.cache/infrastructure/results.json').write_text(json.dumps({'postgres_version':'16.2','redis_version':'8.10.3','checks':results},indent=2))
finally:
    if 'engine' in globals(): engine.dispose()
    with admin.cursor() as cursor:
        cursor.execute('SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=%s AND pid <> pg_backend_pid()', (name,))
        cursor.execute(sql.SQL('DROP DATABASE IF EXISTS {}').format(sql.Identifier(name)))
        cursor.execute(sql.SQL('DROP ROLE IF EXISTS {}').format(sql.Identifier(name)))
    admin.close()
