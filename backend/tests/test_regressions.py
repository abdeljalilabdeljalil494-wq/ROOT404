"""Regression evidence. Mocked transport tests are NOT real provider/isolation tests."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import uuid
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal, check_db_health
from app.core.security import generate_and_store_otp, store_otp, verify_otp, _clear_stores
from app.core.dependencies import _clear_rate_limiter, get_client_ip
from app.models.auth_state import OTPChallenge
from app.models.user import User
from app.models.project import Project
from app.models.submission import Submission
from app.services import email, judge

client = TestClient(app)


def identity():
    _clear_stores()
    _clear_rate_limiter()
    suffix = uuid.uuid4().hex[:12]
    address = f"learner{suffix}@example.com"
    response = client.post('/api/auth/register', json={"email": address, "username": f"learner{suffix}", "display_name": "Learner"})
    assert response.status_code == 200
    code = response.json()['dev_otp']
    response = client.post('/api/auth/verify', json={"email": address, "code": code})
    assert response.status_code == 200
    return address, code, response.json(), {"Authorization": "Bearer " + response.json()['access_token']}


def test_auth_lifecycle_replay_logout_and_empty_dashboard():
    address, code, data, headers = identity()
    assert client.post('/api/auth/verify', json={"email": address, "code": code}).status_code == 400
    assert client.get('/api/auth/me', headers=headers).json()['id'] == data['user']['id']
    with SessionLocal() as db:
        assert db.query(User).filter_by(email=address).one().is_verified
        assert all(value == 0 for group in db.query(User).filter_by(email=address).one().skills.values() for value in group.values())
    dashboard = client.get('/api/dashboard/overview', headers=headers).json()
    assert dashboard['recentActivity'] == []
    assert sum(day['value'] for day in dashboard['weeklyActivity']) == 0
    assert client.get('/api/dashboard/heatmap', headers=headers).json() == [0] * 371
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    assert client.get('/api/auth/me', headers=headers).status_code == 401


def test_expired_otp_and_attempt_lockout():
    address = 'expiry@example.com'
    store_otp(address, '192837')
    with SessionLocal() as db:
        db.get(OTPChallenge, address).expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.commit()
    assert not verify_otp(address, '192837')
    store_otp(address, '192837')
    for _ in range(settings.OTP_MAX_ATTEMPTS):
        assert not verify_otp(address, '000000')
    assert not verify_otp(address, '192837')


def test_concurrent_otp_can_only_be_consumed_once():
    store_otp('concurrent@example.com', '192837')
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: verify_otp('concurrent@example.com', '192837'), range(6)))
    assert sum(results) == 1


def test_delivery_failure_invalidates_challenge(monkeypatch):
    def fail(*args):
        raise email.EmailDeliveryError('unavailable')
    monkeypatch.setattr(email, 'send_otp', fail)
    with pytest.raises(email.EmailDeliveryError):
        generate_and_store_otp('delivery@example.com')
    with SessionLocal() as db:
        assert db.get(OTPChallenge, 'delivery@example.com') is None


def test_smtp_transport_uses_tls_and_does_not_silently_fallback(monkeypatch):
    events = []
    class SMTP:
        def __init__(self, *args, **kwargs): events.append('connect')
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def starttls(self, **kwargs): events.append('tls')
        def login(self, *args): events.append('login')
        def send_message(self, message):
            assert '192837' in message.get_content()
            events.append('send')
    monkeypatch.setattr(settings, 'EMAIL_PROVIDER', 'smtp')
    monkeypatch.setattr(settings, 'SMTP_HOST', 'mail.example.com')
    monkeypatch.setattr(settings, 'SMTP_FROM', 'root404@example.com')
    monkeypatch.setattr(settings, 'SMTP_USERNAME', 'account')
    monkeypatch.setattr(email.smtplib, 'SMTP', SMTP)
    email.send_otp('learner@example.com', '192837')
    assert events == ['connect', 'tls', 'login', 'send']


def test_disabled_judge_cannot_create_submission_or_award_xp():
    _, _, data, headers = identity()
    with SessionLocal() as db:
        before = db.query(Submission).count()
    response = client.post('/api/projects/minishell/submit', headers=headers,
                           json={"files": {"main.c": "int main(void) {return 0;}"}, "language": "c"})
    assert response.status_code == 503
    with SessionLocal() as db:
        assert db.query(Submission).count() == before
        assert db.get(User, data['user']['id']).xp == 0


def test_moulinette_comparison_and_hidden_output_redaction(monkeypatch):
    slug = 'test_' + uuid.uuid4().hex[:8]
    with SessionLocal() as db:
        db.add(Project(slug=slug, name=slug, description='test', test_cases=[
            {"stdin": "secret", "expected_stdout": "42\n", "hidden": True},
            {"stdin": "", "expected_stdout": "wrong"}]))
        db.commit()
    def execute(*args):
        return {"status": "success", "exit_code": 0, "output": "42\n", "error": "", "execution_time": 0.1}
    monkeypatch.setattr(judge, '_execute', execute)
    result = judge.run_moulinette(slug, {"main.c": "int main(){return 0;}"})
    assert result['score'] == 50 and result['passed'] == 1
    assert 'secret' not in str(result) and 'wrong' not in str(result)


def test_private_room_messages_require_membership():
    _, _, _, headers = identity()
    response = client.post('/api/rooms/', headers=headers, json={"name": "Private study", "type": "study", "capacity": 5})
    assert response.status_code == 200
    room_id = response.json()['id']
    _, _, _, outsider = identity()
    assert client.get(f'/api/rooms/{room_id}/messages', headers=outsider).status_code == 403
    assert client.post(f'/api/rooms/{room_id}/messages', headers=outsider, json={"content": "unauthorized"}).status_code == 403


def test_health_query_sqlalchemy2():
    assert check_db_health()


def test_auth_limit_headers_preserved():
    _clear_rate_limiter()
    for _ in range(settings.RATE_LIMIT_AUTH_REQUESTS):
        client.post('/api/auth/login', json={"email": "throttle@example.com"})
    response = client.post('/api/auth/login', json={"email": "throttle@example.com"})
    assert response.status_code == 429
    assert int(response.headers['retry-after']) > 0


def test_project_award_is_once_and_matches_actual_bonus(monkeypatch):
    _, _, data, headers = identity()
    from app.api import projects as project_api
    from app.models.project import UserProjectProgress
    monkeypatch.setattr(project_api, 'run_moulinette', lambda *args: {
        'score': 100, 'tests': [{'name': 'Executed test', 'status': 'pass'}], 'logs': 'Transport stub for award test'})
    payload = {"files": {"main.c": "int main(void){return 0;}"}, "language": "c"}
    first = client.post('/api/projects/get_next_line/submit', headers=headers, json=payload)
    assert first.status_code == 200, first.text
    assert first.json()['xp_earned'] == 1380
    second = client.post('/api/projects/get_next_line/submit', headers=headers, json=payload)
    assert second.status_code == 200
    assert second.json()['xp_earned'] == 0
    with SessionLocal() as db:
        user = db.get(User, data['user']['id'])
        assert user.xp == 1380 and user.projects_done == 1
    monkeypatch.setattr(project_api, 'run_moulinette', lambda *args: {'score': 0, 'tests': [], 'logs': 'failed execution stub'})
    third = client.post('/api/projects/get_next_line/submit', headers=headers, json=payload)
    assert third.status_code == 200 and third.json()['status'] == 'passed'


def test_seed_mutations_require_admin():
    _, _, _, headers = identity()
    for path in ('projects', 'rooms', 'piscine'):
        assert client.post(f'/api/{path}/seed').status_code == 401
        assert client.post(f'/api/{path}/seed', headers=headers).status_code == 403


def test_forwarded_header_does_not_bypass_auth_limiter():
    _clear_rate_limiter()
    for i in range(settings.RATE_LIMIT_AUTH_REQUESTS):
        client.post('/api/auth/login', json={'email': f'learner{i}@example.com'}, headers={'X-Forwarded-For': f'192.0.2.{i}'})
    response = client.post('/api/auth/login', json={'email': 'another@example.com'}, headers={'X-Forwarded-For': '198.51.100.1'})
    assert response.status_code == 429


def test_ai_provider_disabled_is_not_a_fake_answer(monkeypatch):
    from app.services.ai_provider import ask_provider
    monkeypatch.setattr(settings, 'AI_PROVIDER', 'disabled')
    with pytest.raises(HTTPException) as error:
        ask_provider('Why?', 2, {})
    assert error.value.status_code == 503
