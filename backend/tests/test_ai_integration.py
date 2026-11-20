"""Real API/SQL wiring with simulated HTTP provider. No live AI calls are made."""
import json
import uuid
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.dependencies import _clear_rate_limiter
from app.core.security import _clear_stores
from app.services import ai_provider

client = TestClient(app)


def account():
    _clear_stores()
    _clear_rate_limiter()
    suffix = uuid.uuid4().hex[:12]
    email = f'ai{suffix}@example.com'
    response = client.post('/api/auth/register', json={'email': email, 'username': f'ai{suffix}', 'display_name': 'Learner'})
    assert response.status_code == 200
    verified = client.post('/api/auth/verify', json={'email': email, 'code': response.json()['dev_otp']})
    assert verified.status_code == 200
    return {'Authorization': 'Bearer ' + verified.json()['access_token']}


def provider(monkeypatch, handler):
    real_client = httpx.Client
    monkeypatch.setattr(settings, 'AI_PROVIDER', 'openai')
    monkeypatch.setattr(settings, 'OPENAI_API_KEY', 'test-not-a-real-key')
    def create(**kwargs):
        assert kwargs['trust_env'] is False and kwargs['follow_redirects'] is False
        return real_client(transport=httpx.MockTransport(handler), **kwargs)
    monkeypatch.setattr(ai_provider.httpx, 'Client', create)


def test_provider_request_context_and_persisted_private_history(monkeypatch):
    headers = account()
    def handler(request):
        assert str(request.url) == 'https://api.openai.com/v1/chat/completions'
        assert request.headers['authorization'] == 'Bearer test-not-a-real-key'
        payload = json.loads(request.content)
        assert payload['model'] == settings.AI_MODEL and payload['max_tokens'] == 1000
        assert 'do not simply solve' in payload['messages'][0]['content']
        assert 'int main' in payload['messages'][1]['content']
        return httpx.Response(200, json={'choices': [{'message': {'content': 'What does the pointer reference?'}}]})
    provider(monkeypatch, handler)
    response = client.post('/api/ai/ask', headers=headers,
        json={'message': 'Explain my pointer', 'code': 'int main(void) {return 0;}', 'level': 2})
    assert response.status_code == 200, response.text
    assert response.json()['provider'] == 'openai'
    assert response.json()['execution_verified'] is False
    history = client.get('/api/ai/history', headers=headers).json()
    assert [item['role'] for item in history] == ['user', 'ai']
    assert history[0]['text'] == 'Explain my pointer'
    assert 'int main' not in str(history)
    outsider = account()
    assert client.get('/api/ai/history', headers=outsider).json() == []


@pytest.mark.parametrize('path', ['/api/ai/review', '/api/judge/review'])
def test_both_review_routes_use_provider_not_random_metrics(monkeypatch, path):
    headers = account()
    provider(monkeypatch, lambda request: httpx.Response(200, json={'choices': [{'message': {'content': 'Try testing the empty input.'}}]}))
    response = client.post(path, headers=headers, json={'code': 'print(42)', 'language': 'python'})
    assert response.status_code == 200
    assert response.json()['method'] == 'provider_advice'
    assert 'metrics' not in response.json() and 'score' not in response.json()
    assert len(client.get('/api/ai/history', headers=headers).json()) == 2


@pytest.mark.parametrize('path', ['/api/ai/ask', '/api/ai/review', '/api/judge/review'])
def test_missing_provider_returns_unavailable_and_no_fake_history(monkeypatch, path):
    headers = account()
    monkeypatch.setattr(settings, 'AI_PROVIDER', 'disabled')
    payload = {'message': 'Help me'} if path.endswith('/ask') else {'code': 'print(42)'}
    response = client.post(path, headers=headers, json=payload)
    assert response.status_code == 503
    assert client.get('/api/ai/history', headers=headers).json() == []


@pytest.mark.parametrize('status,body', [
    (429, {'error': 'rate limited'}), (500, {'error': 'failure'}),
    (302, {}), (200, {'choices': []}), (200, {'choices': [{'message': {'content': ''}}]}),
])
def test_provider_failure_has_no_template_fallback(monkeypatch, status, body):
    provider(monkeypatch, lambda request: httpx.Response(status, json=body, headers={'location': 'https://example.com'}))
    with pytest.raises(HTTPException) as error:
        ai_provider.ask_provider('Question', 2, {})
    assert error.value.status_code == 503


def test_provider_response_limit(monkeypatch):
    provider(monkeypatch, lambda request: httpx.Response(200, content=b'x' * 262145))
    with pytest.raises(HTTPException) as error:
        ai_provider.ask_provider('Question', 2, {})
    assert error.value.status_code == 503


def test_account_budget_shared_by_ask_and_review_aliases(monkeypatch):
    headers = account()
    monkeypatch.setattr(settings, 'AI_REQUESTS_PER_HOUR', 2)
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={'choices': [{'message': {'content': 'Consider an edge case.'}}]})
    provider(monkeypatch, handler)
    assert client.post('/api/ai/ask', headers=headers, json={'message': 'Help'}).status_code == 200
    assert client.post('/api/ai/review', headers=headers, json={'code': 'print(42)'}).status_code == 200
    response = client.post('/api/judge/review', headers=headers, json={'code': 'print(42)'})
    assert response.status_code == 429 and int(response.headers['retry-after']) > 0
    assert len(calls) == 2


def test_connect_failure_retries_once_but_read_timeout_never_replays_paid_request(monkeypatch):
    headers = account()
    calls = []
    def recover(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.ConnectError('test connection failure', request=request)
        return httpx.Response(200, json={'choices': [{'message': {'content': 'Connection recovered.'}}]})
    provider(monkeypatch, recover)
    response = client.post('/api/ai/ask', headers=headers, json={'message': 'Explain pointers'})
    assert response.status_code == 200 and len(calls) == 2
    # Replace the underlying mock transport without nesting the client factory.
    monkeypatch.undo()
    calls = []
    def accepted_but_timed_out(request):
        calls.append(request)
        raise httpx.ReadTimeout('test read timeout', request=request)
    provider(monkeypatch, accepted_but_timed_out)
    response = client.post('/api/ai/ask', headers=headers, json={'message': 'Explain pointers'})
    assert response.status_code == 503 and len(calls) == 1
