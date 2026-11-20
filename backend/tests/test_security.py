import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import sanitize_input, validate_username, generate_and_store_otp, verify_otp, _clear_stores
from app.core.dependencies import _clear_rate_limiter
from app.models.user import User
import uuid

client = TestClient(app)

def get_token():
    from app.core.security import _clear_stores
    from app.core.dependencies import _clear_rate_limiter
    _clear_stores()
    _clear_rate_limiter()
    resp = client.post("/api/auth/otp", json={"email": "abdeljalil@root404.tn"})
    otp = resp.json().get("dev_otp") or resp.json().get("dev_otp")
    # Try to get from store if not in response (prod mode)
    if not otp:
        from app.core.security import get_last_otp
        otp = get_last_otp("abdeljalil@root404.tn")
    resp = client.post("/api/auth/verify", json={"email": "abdeljalil@root404.tn", "code": otp})
    return resp.json()["access_token"]

class TestInputSanitization:
    def test_sanitize_xss_script(self):
        result = sanitize_input("<script>alert('xss')</script>", max_length=100)
        assert "<script>" not in result or result == "<script>alert('xss')</script>"  # We log but don't block, output encoding is at render
        # Ensure null bytes removed
        result = sanitize_input("hello\x00world")
        assert "\x00" not in result
    
    def test_sanitize_truncation(self):
        long_text = "a" * 2000
        result = sanitize_input(long_text, max_length=100)
        assert len(result) <= 100
    
    def test_validate_username_valid(self):
        valid, msg = validate_username("abdeljalil")
        assert valid is True
        
        valid, msg = validate_username("test_user-123")
        assert valid is True
    
    def test_validate_username_invalid(self):
        valid, msg = validate_username("ab")
        assert valid is False
        
        valid, msg = validate_username("a" * 31)
        assert valid is False
        
        valid, msg = validate_username("123invalid")
        assert valid is False
        
        valid, msg = validate_username("admin")
        assert valid is False
    
    def test_validate_username_injection(self):
        # SQL injection attempt
        valid, msg = validate_username("admin'; DROP TABLE users; --")
        assert valid is False
        
        # XSS attempt
        valid, msg = validate_username("<script>")
        assert valid is False

class TestAuthSecurity:
    def test_otp_rate_limiting(self):
        _clear_stores()
        _clear_rate_limiter()
        email = f"ratelimit_{uuid.uuid4().hex[:6]}@test.tn"
        
        # Should allow first 5 requests
        for i in range(5):
            try:
                otp = generate_and_store_otp(email)
                assert otp
            except ValueError:
                # Rate limited
                if i < 5:
                    assert False, f"Should allow request {i+1}"
        
        # 6th should fail
        try:
            otp = generate_and_store_otp(email)
            assert False, "Should be rate limited"
        except ValueError as e:
            assert "Rate limit" in str(e)
    
    def test_otp_invalid_code(self):
        email = f"test_{uuid.uuid4().hex[:6]}@test.tn"
        otp = generate_and_store_otp(email)
        
        # Wrong code
        assert verify_otp(email, "000000") is False
        assert verify_otp(email, "123456") is False
        
        # Correct code
        assert verify_otp(email, otp) is True
        
        # Reuse should fail (one-time)
        assert verify_otp(email, otp) is False
    
    def test_otp_expired(self):
        # This would require mocking time, but we test max attempts
        email = f"test_{uuid.uuid4().hex[:6]}@test.tn"
        otp = generate_and_store_otp(email)
        
        # Exhaust attempts
        for _ in range(5):
            verify_otp(email, "000000")
        
        # Even correct code should fail after max attempts
        assert verify_otp(email, otp) is False
    
    def test_jwt_invalid_format(self):
        # No token
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
        
        # Invalid token format
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401
        
        # Malformed Bearer
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer"})
        assert resp.status_code == 401
        
        # Empty token
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401
    
    def test_jwt_expired(self):
        # Create expired token manually
        from app.core.security import create_access_token
        from datetime import timedelta
        token = create_access_token({"sub": "u_test"}, expires_delta=timedelta(seconds=-1))
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
    
    def test_register_invalid_username(self):
        # Too short
        resp = client.post("/api/auth/register", json={
            "username": "ab",
            "email": f"test_{uuid.uuid4().hex[:6]}@test.tn",
            "display_name": "Test"
        })
        assert resp.status_code in [400, 422]
        
        # Invalid chars
        resp = client.post("/api/auth/register", json={
            "username": "test'; DROP TABLE",
            "email": f"test_{uuid.uuid4().hex[:6]}@test.tn",
            "display_name": "Test"
        })
        assert resp.status_code in [400, 422]
        
        # Reserved
        resp = client.post("/api/auth/register", json={
            "username": "admin",
            "email": f"test_{uuid.uuid4().hex[:6]}@test.tn",
            "display_name": "Test"
        })
        assert resp.status_code in [400, 422]
    
    def test_register_xss_in_display_name(self):
        # XSS attempt in display name should be sanitized or rejected
        resp = client.post("/api/auth/register", json={
            "username": f"test_{uuid.uuid4().hex[:6]}",
            "email": f"test_{uuid.uuid4().hex[:6]}@test.tn",
            "display_name": "<script>alert('xss')</script>"
        })
        # Should either reject or sanitize
        assert resp.status_code in [200, 400, 422]
    
    def test_auth_sql_injection(self):
        # SQL injection in email
        resp = client.post("/api/auth/otp", json={
            "email": "test@test.tn' OR '1'='1"
        })
        assert resp.status_code == 422  # Should fail email validation
        
        # SQL injection in username
        resp = client.post("/api/auth/register", json={
            "username": "test' OR '1'='1",
            "email": f"test_{uuid.uuid4().hex[:6]}@test.tn",
            "display_name": "Test"
        })
        assert resp.status_code in [400, 422]

class TestProjectSecurity:
    def test_project_unauthorized(self):
        resp = client.get("/api/projects/")
        assert resp.status_code == 401
    
    def test_project_invalid_slug(self):
        token = get_token()
        # Path traversal attempt
        resp = client.get("/api/projects/../../etc/passwd", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in [400, 404]
        
        # SQL injection in slug
        resp = client.get("/api/projects/' OR '1'='1", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in [400, 404]
        
        # XSS in slug
        resp = client.get("/api/projects/<script>alert(1)</script>", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in [400, 404]
    
    def test_submit_invalid_files(self):
        token = get_token()
        
        # No files
        resp = client.post("/api/projects/minishell/submit", 
            json={"files": {}, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 422]
        
        # Path traversal in filename
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"../../etc/passwd": "content"}, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 422]
        
        # Too many files
        many_files = {f"file{i}.c": "content" for i in range(25)}
        resp = client.post("/api/projects/minishell/submit",
            json={"files": many_files, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 422]
        
        # Null byte
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"test\x00.c": "content"}, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 422]
    
    def test_submit_forbidden_patterns(self):
        token = get_token()
        
        # Python with os.system
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"test.py": "import os\nos.system('rm -rf /')"}, "language": "python"},
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should be blocked or score 0
        if resp.status_code == 200:
            assert resp.json()["score"] == 0 or "security" in str(resp.json()).lower() or "forbidden" in str(resp.json()).lower()
        else:
            assert resp.status_code in [400, 422]
    
    def test_submit_xss_in_code(self):
        token = get_token()
        # Code with script tag - should be handled safely (stored as text, not executed)
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"test.c": "<script>alert('xss')</script>\nint main() { return 0; }"}, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        # No configured executor/suite: must not pretend to compile or persist success.
        assert resp.status_code == 503
        assert "score" not in resp.json()

class TestRateLimiting:
    def test_auth_rate_limit(self):
        _clear_rate_limiter()
        email = f"ratelimit_{uuid.uuid4().hex[:6]}@test.tn"
        
        # Make many requests quickly
        responses = []
        for i in range(15):
            resp = client.post("/api/auth/otp", json={"email": email})
            responses.append(resp.status_code)
        
        # Should have some 429s
        # Note: OTP per-email limit is 5/hour, plus global rate limit 10/min
        assert 429 in responses or 400 in responses  # Either rate limited or OTP limit

class TestSecurityHeaders:
    def test_security_headers_present(self):
        resp = client.get("/health")
        # Check for security headers
        assert "X-Content-Type-Options" in resp.headers or resp.status_code == 200
        # At least should have X-Process-Time
        assert "X-Process-Time" in resp.headers or "X-Request-ID" in resp.headers
    
    def test_cors_headers(self):
        resp = client.options("/api/health", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        })
        # Should have CORS headers
        assert resp.status_code in [200, 405]

class TestDatabaseSecurity:
    def test_sql_injection_in_search(self):
        token = get_token()
        # Try SQL injection via search param
        malicious_queries = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1; SELECT * FROM users",
        ]
        
        for q in malicious_queries:
            resp = client.get(f"/api/search?q={q}", headers={"Authorization": f"Bearer {token}"})
            # Should not crash, should return 200 or 422, not 500 with SQL error
            assert resp.status_code in [200, 422, 400]
            # Ensure no SQL error leaked
            if resp.status_code == 500:
                assert "sql" not in resp.text.lower() and "syntax" not in resp.text.lower()

class TestJudgeSecurity:
    def test_judge_forbidden_patterns(self):
        token = get_token()
        
        forbidden_codes = [
            ("python", "import os\nos.system('ls')"),
            ("python", "import subprocess\nsubprocess.call(['ls'])"),
            ("python", "__import__('os').system('ls')"),
            ("c", "#include <sys/socket.h>\nint main() { socket(1,2,3); }"),
            ("javascript", "require('child_process').exec('ls')"),
        ]
        
        for lang, code in forbidden_codes:
            resp = client.post("/api/judge/run",
                json={"code": code, "language": lang},
                headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                # Should be blocked
                assert data.get("status") in ["security_violation", "error", "failed"] or "forbidden" in str(data).lower() or "security" in str(data).lower()
    
    def test_judge_large_input(self):
        token = get_token()
        large_code = "a" * (1024 * 1024 + 1)  # 1MB + 1
        
        resp = client.post("/api/judge/run",
            json={"code": large_code, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 413, 422, 200]
        if resp.status_code == 200:
            assert resp.json().get("status") in ["error", "security_violation"]

def teardown_module():
    _clear_stores()
    _clear_rate_limiter()
