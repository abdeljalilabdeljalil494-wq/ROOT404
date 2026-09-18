# Security Policy for ROOT404

## Overview
ROOT404 is a peer-learning platform with security-first design. This document outlines security measures, hardening, and reporting.

## Security Measures Implemented

### 1. Container Hardening (docker-compose.yml)
- **No hardcoded secrets**: All secrets via environment variables `${VAR:?required}` / `${VAR:-default}`
- **Read-only filesystems**: `read_only: true` with `tmpfs` for `/tmp` (noexec, nosuid)
- **No new privileges**: `security_opt: no-new-privileges:true`
- **Capability dropping**: `cap_drop: ALL` with minimal `cap_add`
- **User namespacing**: Non-root users (appuser uid 1000, nginx user)
- **Resource limits**: CPU, memory, PIDs limited per service
- **Network segmentation**: 
  - `backend_network` (172.28.0.0/16) - db, redis, backend, runner
  - `frontend_network` - frontend, backend
  - `no_internet` - runner isolated, internal:true
- **Port binding**: `127.0.0.1:port` not `0.0.0.0` to prevent external exposure
- **Healthchecks**: With start_period to prevent premature traffic

### 2. Backend Dockerfile Hardening
- **Multi-stage build**: Builder with gcc, runtime only libpq5+curl
- **Setuid removal**: `find / -perm -4000 -delete` and removal of su, wget, curl in runner
- **Non-root user**: `useradd -s /bin/false -u 1000 appuser`
- **File permissions**: `chown 750`, `chmod 700` for cache, `go-w` for nginx
- **Cache cleaning**: `rm -rf /var/lib/apt/lists/*`, pip cache, `__pycache__`
- **Healthcheck**: curl/wget with timeout

### 3. Frontend Dockerfile Hardening
- **Build stage**: `npm ci --ignore-scripts` to prevent malicious scripts, cache clean, remove sourcemaps
- **Nginx hardening**:
  - Security headers: `X-Content-Type-Options nosniff`, `X-Frame-Options DENY`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`, `CSP`
  - Gzip enabled
  - SPA fallback with `try_files`
  - Immutable caching for static assets (1y)
  - `/api` proxy with timeouts (10s connect, 30s read), `client_max_body_size 10m`, buffering limits
  - Block hidden files (`~ /\.`) and sensitive files (`.env`, `.git`)
  - `USER nginx` (non-root)
  - Healthcheck via wget spider

### 4. Authentication & Authorization
- **OTP system**: 
  - Thread-safe with `RLock`
  - Rate limit 5/hour per email
  - `secrets.choice` for secure OTP generation
  - `hmac.compare_digest` for constant-time comparison
  - One-time use, 5 min expiry, max 3 attempts
  - `dev_otp` only in non-production
- **JWT**:
  - `iss`, `nbf`, `jti` claims
  - Short expiry (30 min default)
  - Secure secret validation (min 32 chars in prod, required)
  - Token length check (10-2048 chars)
- **Account states**: `is_active` check, Black Hole (frozen) returns 403
- **Rate limiting**: 
  - Auth: 10/min per IP
  - Judge: 20/min per user
  - Search: 30/min
  - Sliding window with thread-safe `RateLimiter`
  - `Retry-After` header

### 5. Input Validation & Sanitization
- **Pydantic models**: `Field(max_length)`, `pattern` regex, `field_validator`
- **Sanitization**: `sanitize_input` removes null bytes, truncates, logs suspicious patterns
- **Username validation**: Alphanumeric + _-, 3-30 chars, reserved list (admin, root, etc.), no leading digit
- **Email validation**: Format check, disposable email block, max length
- **File validation**:
  - Filename: max 100 chars, no `..`, `/`, `\`, null byte, path traversal
  - File size: 1MB per file, 5MB total, 20 files max
  - Language whitelist: c, cpp, python, js
  - Forbidden patterns per language (os.system, subprocess, socket, etc.)
- **Query sanitization**: `re.escape` for search, allowed list for status, slug regex `^[a-zA-Z0-9_-]+$`
- **Output truncation**: Logs 10k stored, 5k returned, to prevent DoS

### 6. Database Security
- **Parameterized queries**: SQLAlchemy ORM prevents SQL injection
- **Connection pooling**: `QueuePool` with size limits, timeout, recycle
- **SQLite hardening**: `PRAGMA foreign_keys=ON`, WAL mode, `synchronous=NORMAL`
- **Error handling**: `SQLAlchemyError` returns 503, not 500 with details
- **Indexes**: For performance and to prevent full table scans
- **CheckConstraints**: Level 0-21, XP >=0, reputation/integrity 0-100, etc.
- **Foreign keys**: `ondelete CASCADE/SET NULL` with `passive_deletes`
- **String lengths**: Explicit limits (32, 30, 254, 50, 100, 500) to prevent overflow

### 7. Judge Sandbox Security
- **Whitelist**: `ALLOWED_LANGUAGES`, `RUNNERS` registry
- **Forbidden patterns**: Per-language blocklist (os, subprocess, socket, etc.)
- **Input validation**: Path traversal via `relative_to`, null byte, size limits
- **Isolation**:
  - Temp dir with `mkdtemp` mode 0o700, files 0o600
  - Env `PATH` sanitized
  - Timeout clamped
  - Output truncation 10k stdout, 5k stderr
  - Resource limits: 30s, 512M, 64 files, 64 pids, 10MB file
- **Docker**: `ubuntu:22.04` hardened, remove setuid, rm wget/curl/su, judge uid 1000 /bin/false, `chmod 700`

### 8. API Security
- **Security headers** (main.py):
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: geolocation=(), microphone=(), camera=()`
  - `Content-Security-Policy: default-src 'self'` (prod)
  - `Strict-Transport-Security` in prod
  - `Server` header masked
- **CORS**: No `*` in prod, explicit methods, credentials handling
- **Request size**: 10MB limit
- **Request ID**: `X-Request-ID` for audit
- **Audit logging**: IP, method, path, status, duration
- **Error handling**: No stack traces in prod, 503 for DB failures

### 9. Frontend Security
- **API hardening**:
  - Input sanitization (null bytes, truncation)
  - File validation (name, size, count)
  - Language whitelist
  - JWT format validation
  - `X-Requested-With` header for CSRF
  - Rate limit handling (429 with Retry-After)
  - Error handling without leaking details
  - Security header checks in dev
- **ErrorBoundary**: Catches React errors, shows safe fallback, no stack in prod
- **XSS prevention**: Output encoding via React (auto), sanitization of user inputs
- **CSRF**: SameSite cookies (if used), custom header

### 10. Testing & Validation
- **Backend tests**: 53 tests covering:
  - Unauthorized access (401)
  - Missing parameters (422)
  - Invalid formats (email, username)
  - Nonexistent resources (404)
  - Large payloads (400/413)
  - Path traversal (400/422)
  - XSS attempts (200/400 with safe handling)
  - SQL injection (200/400 without leak)
  - Judge security (forbidden patterns blocked)
  - Rate limiting (429)
  - Security headers
  - CORS
- **Frontend tests**: 14 tests covering:
  - Token storage
  - Input validation
  - File validation
  - Forbidden patterns
  - XSS sanitization
  - Critical flows (auth, submission, room creation)

## Secrets Management
- **No hardcoded secrets**: All via env vars
- **.env.example**: Template with placeholders
- **.gitignore**: `.env` excluded
- **Docker**: Secrets via env, not baked into images
- **Production**: Use vault (HashiCorp Vault, AWS Secrets Manager, etc.)

## Vulnerability Reporting
If you discover a security vulnerability, please:
1. **DO NOT** open a public issue
2. Email security@root404.tn with details
3. Include steps to reproduce
4. Allow 90 days for fix before public disclosure

## Security Checklist for Production
- [ ] Set `SECRET_KEY` to random 32+ chars (`openssl rand -hex 32`)
- [ ] Set strong `POSTGRES_PASSWORD` and `REDIS_PASSWORD`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `CORS_ORIGINS` to your domain only
- [ ] Enable HTTPS with valid cert (HSTS will be auto-enabled)
- [ ] Configure SMTP for OTP emails (disable dev_otp)
- [ ] Set up monitoring (Sentry, logs)
- [ ] Enable backups for DB
- [ ] Review `docker-compose.yml` resource limits for your workload
- [ ] Scan images with Trivy/Clair
- [ ] Set up WAF (Cloudflare, etc.)
- [ ] Configure log retention and audit

## Known Limitations
- OTP via email not implemented (dev_otp used in dev)
- No 2FA beyond OTP
- Rate limiting in-memory (use Redis in prod for multi-instance)
- No WAF in compose (use external)
- Frontend mock mode (`VITE_USE_MOCK`) should be false in prod

## Dependencies
- Keep dependencies updated: `pip-audit`, `npm audit`
- Pinned versions in requirements.txt and package.json
- No `*` versions

## Compliance
- GDPR: User data minimization, right to delete (to be implemented)
- Logging: No sensitive data in logs (passwords, tokens redacted)
- Audit: All critical actions logged with IP and user ID
