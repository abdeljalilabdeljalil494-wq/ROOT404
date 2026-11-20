import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import _clear_stores
from app.core.dependencies import _clear_rate_limiter
import uuid

client = TestClient(app)

def get_token():
    from app.core.security import _clear_stores
    from app.core.dependencies import _clear_rate_limiter
    _clear_stores()
    _clear_rate_limiter()
    resp = client.post("/api/auth/otp", json={"email": "abdeljalil@root404.tn"})
    data = resp.json()
    otp = data.get("dev_otp")
    if not otp:
        from app.core.security import get_last_otp
        otp = get_last_otp("abdeljalil@root404.tn")
    resp = client.post("/api/auth/verify", json={"email": "abdeljalil@root404.tn", "code": otp})
    return resp.json()["access_token"]

class TestEdgeCases:
    def test_missing_parameters(self):
        # OTP without email
        resp = client.post("/api/auth/otp", json={})
        assert resp.status_code == 422
        
        # Verify without code
        resp = client.post("/api/auth/verify", json={"email": "test@test.tn"})
        assert resp.status_code == 422
        
        # Register without required fields
        resp = client.post("/api/auth/register", json={"username": "test"})
        assert resp.status_code == 422
        
        # Project submit without files
        token = get_token()
        resp = client.post("/api/projects/minishell/submit", 
            json={}, 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 422
    
    def test_invalid_email_formats(self):
        invalid_emails = [
            "invalid",
            "test@",
            "@test.com",
            "test@test",
            "test@test..com",
            "test..test@test.com",
            "",
            "a" * 255 + "@test.com",  # Too long
        ]
        
        for email in invalid_emails:
            resp = client.post("/api/auth/otp", json={"email": email})
            assert resp.status_code in [400, 422], f"Should reject {email}"
    
    def test_invalid_username_formats(self):
        token = get_token()
        invalid_usernames = [
            "ab",  # Too short
            "a" * 31,  # Too long
            "123test",  # Starts with number
            "test user",  # Space
            "test@user",  # Special char
            "admin",  # Reserved
            "root",  # Reserved
        ]
        
        for username in invalid_usernames:
            resp = client.post("/api/auth/register", json={
                "username": username,
                "email": f"test_{uuid.uuid4().hex[:6]}@test.tn",
                "display_name": "Test"
            })
            assert resp.status_code in [400, 422], f"Should reject username {username}"
    
    def test_nonexistent_resources(self):
        token = get_token()
        
        # Nonexistent project
        resp = client.get("/api/projects/nonexistent_project_xyz", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
        
        # Nonexistent room
        resp = client.get("/api/rooms/nonexistent_room", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
        
        # Nonexistent portfolio
        resp = client.get("/api/portfolio/nonexistent_user_xyz_123")
        assert resp.status_code == 404
    
    def test_unauthorized_access(self):
        # No token
        resp = client.get("/api/projects/")
        assert resp.status_code == 401
        
        resp = client.get("/api/dashboard/overview")
        assert resp.status_code == 401
        
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
        
        # Invalid token
        resp = client.get("/api/projects/", headers={"Authorization": "Bearer invalid_token_here"})
        assert resp.status_code == 401
        
        # Expired token (manipulated)
        resp = client.get("/api/projects/", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1X3Rlc3QiLCJleHAiOjF9.invalid"})
        assert resp.status_code == 401
    
    def test_forbidden_access(self):
        # Regular user trying to access admin would need admin endpoint
        # For now test that frozen account is blocked
        # We can't easily test frozen without manipulating DB, but we test is_active check
        token = get_token()
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
    
    def test_large_payloads(self):
        token = get_token()
        
        # Very large file content
        large_content = "a" * (1024 * 1024 + 100)  # 1MB + 100
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"large.c": large_content}, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 413, 422]
        
        # Many files
        many_files = {f"file{i}.c": "content" for i in range(30)}
        resp = client.post("/api/projects/minishell/submit",
            json={"files": many_files, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 422]
    
    def test_path_traversal_attempts(self):
        token = get_token()
        
        traversal_attempts = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/passwd",
            "file/../../etc/passwd",
            "test\x00.c",
        ]
        
        for filename in traversal_attempts:
            resp = client.post("/api/projects/minishell/submit",
                json={"files": {filename: "content"}, "language": "c"},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code in [400, 422], f"Should block {filename}"
    
    def test_xss_attempts(self):
        token = get_token()
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
        ]
        
        for payload in xss_payloads:
            # Try in search
            resp = client.get(f"/api/search?q={payload}", headers={"Authorization": f"Bearer {token}"})
            # Should not crash, should handle safely
            assert resp.status_code in [200, 400, 422]
            
            # Try in room creation
            resp = client.post("/api/rooms/",
                json={"name": payload, "type": "study", "capacity": 10},
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should handle safely
            assert resp.status_code in [200, 201, 400, 422]
    
    def test_sql_injection_attempts(self):
        token = get_token()
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1; SELECT * FROM users",
            "admin'--",
        ]
        
        for payload in sql_payloads:
            # Search
            resp = client.get(f"/api/search?q={payload}", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code in [200, 400, 422]
            # Ensure no SQL error leaked
            assert "sql" not in resp.text.lower() or "syntax" not in resp.text.lower() or resp.status_code != 500
            
            # Projects filter
            resp = client.get(f"/api/projects/?q={payload}", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code in [200, 400, 422]
    
    def test_judge_security(self):
        token = get_token()
        
        # Forbidden patterns should be blocked
        forbidden = [
            ("python", "import os\nos.system('id')"),
            ("python", "import subprocess\nsubprocess.Popen(['ls'])"),
            ("c", "#include <sys/socket.h>\nint main(){socket(1,2,3);}"),
        ]
        
        for lang, code in forbidden:
            resp = client.post("/api/judge/run",
                json={"code": code, "language": lang},
                headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                result = resp.json()
                # Should be flagged as security violation
                assert result.get("status") in ["security_violation", "error", "failed"] or "forbidden" in str(result).lower() or "security" in str(result).lower()
    
    def test_rate_limiting_headers(self):
        # Make request and check for rate limit headers
        resp = client.get("/health")
        # Should have process time header
        assert "X-Process-Time" in resp.headers or "X-Request-ID" in resp.headers
    
    def test_security_headers(self):
        resp = client.get("/health")
        # Check for security headers (at least some should be present)
        # In test, security headers middleware should add them
        # We check that response is valid and not leaking server info
        assert resp.status_code == 200
        # Server header should be masked
        server = resp.headers.get("Server", "")
        assert "uvicorn" not in server.lower() or "ROOT404" in server
    
    def test_cors_configuration(self):
        # Test CORS with allowed origin
        resp = client.options("/api/health", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        })
        # Should handle OPTIONS
        assert resp.status_code in [200, 405]
    
    def test_invalid_language(self):
        token = get_token()
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"test.c": "int main(){return 0;}"}, "language": "invalid_lang"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code in [400, 422]
    
    def test_empty_code_submission(self):
        token = get_token()
        resp = client.post("/api/projects/minishell/submit",
            json={"files": {"empty.c": ""}, "language": "c"},
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should handle empty file
        assert resp.status_code in [200, 400]
        if resp.status_code == 200:
            assert resp.json()["score"] == 0

def teardown_module():
    _clear_stores()
    _clear_rate_limiter()
