#!/usr/bin/env bash
# Read-only checks of an already started operator-configured staging stack.
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
: "${ROOT404_STACK_ENV:?Private env file outside checkout required}"
: "${ROOT404_STACK_URL:?Staging HTTP(S) origin required}"
[[ "$ROOT404_STACK_ENV" = /* && "$ROOT404_STACK_ENV" != "$ROOT"* ]] || exit 2
docker compose --env-file "$ROOT404_STACK_ENV" config --quiet
# No docker inspect/env/raw compose config/logs in artifacts: those may contain secrets.
docker compose --env-file "$ROOT404_STACK_ENV" ps --format '{{.Service}} {{.State}} {{.Health}}'
"$PYTHON" - <<'PY'
import os,httpx
from urllib.parse import urlsplit
url=os.environ['ROOT404_STACK_URL'].rstrip('/')
p=urlsplit(url)
assert p.scheme in {'http','https'} and not p.username and not p.password and p.path in {'','/'}
with httpx.Client(timeout=15,trust_env=False,follow_redirects=False) as client:
    for path in ['/health','/ready','/api/health','/api/auth/me']:
        response=client.get(url+path)
        assert response.status_code==(401 if path.endswith('/me') else 200)
print('PASS: same-origin frontend/API health and anonymous authentication boundary')
PY
