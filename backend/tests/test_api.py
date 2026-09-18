import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.services.skill_graph import SkillGraphService
from app.core.security import _clear_stores
from app.core.dependencies import _clear_rate_limiter

client = TestClient(app)

def get_token_for_demo():
    # Clear rate limiting for tests
    _clear_stores()
    _clear_rate_limiter()
    # Request OTP for demo user
    resp = client.post("/api/auth/otp", json={"email": "abdeljalil@root404.tn"})
    assert resp.status_code == 200, f"OTP failed: {resp.text}"
    data = resp.json()
    otp = data.get("dev_otp")
    if not otp:
        from app.core.security import get_last_otp
        otp = get_last_otp("abdeljalil@root404.tn")
    assert otp, f"No OTP: {data}"
    resp = client.post("/api/auth/verify", json={"email": "abdeljalil@root404.tn", "code": otp})
    assert resp.status_code == 200, f"Verify failed: {resp.text}"
    return resp.json()["access_token"]

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_api_health():
    _clear_rate_limiter()
    resp = client.get("/api/health")
    assert resp.status_code == 200

def test_auth_flow():
    _clear_stores()
    _clear_rate_limiter()
    # New user registration
    import uuid
    email = f"test_{uuid.uuid4().hex[:6]}@root404.tn"
    username = f"test_{uuid.uuid4().hex[:6]}"
    
    resp = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "display_name": "Test User",
        "full_name": "Test User Full",
        "campus": "Tunis"
    })
    assert resp.status_code == 200
    otp = resp.json().get("dev_otp")
    if not otp:
        from app.core.security import get_last_otp
        otp = get_last_otp(email)
    assert otp
    
    resp = client.post("/api/auth/verify", json={"email": email, "code": otp})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

def test_projects_list():
    token = get_token_for_demo()
    resp = client.get("/api/projects/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 5

def test_dashboard():
    token = get_token_for_demo()
    resp = client.get("/api/dashboard/overview", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "stats" in resp.json()
    assert "user" in resp.json()

def test_judge_moulinette():
    token = get_token_for_demo()
    resp = client.post("/api/judge/moulinette/minishell", 
        json={
            "project_slug": "minishell",
            "files": {"minishell.c": "int main() { return 0; }"},
            "language": "c"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "score" in resp.json()
    assert "tests" in resp.json()

def test_ai_ask():
    token = get_token_for_demo()
    resp = client.post("/api/ai/ask",
        json={"message": "Why segfault?", "level": 2},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "text" in resp.json() or "role" in resp.json()

def test_leaderboard():
    _clear_rate_limiter()
    resp = client.get("/api/leaderboard/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_rooms():
    token = get_token_for_demo()
    resp = client.get("/api/rooms/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_analytics():
    token = get_token_for_demo()
    resp = client.get("/api/analytics/overview", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "velocity" in resp.json()

def test_portfolio():
    _clear_rate_limiter()
    resp = client.get("/api/portfolio/abdeljalil")
    # May be 200 or 404 if user not seeded yet, but should not crash
    assert resp.status_code in [200, 404]

def test_hiring():
    _clear_rate_limiter()
    resp = client.get("/api/hiring/companies")
    assert resp.status_code == 200

def test_exam():
    token = get_token_for_demo()
    resp = client.get("/api/exam/tracks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def teardown_module():
    _clear_stores()
    _clear_rate_limiter()
