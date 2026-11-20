#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
"$PYTHON" - <<'PY'
# Presence/shape validation ONLY; never imports settings or reads a real .env.
import os,json
from urllib.parse import urlsplit
checks={
'google':['GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET','GOOGLE_REDIRECT_URI'],
'github':['GITHUB_CLIENT_ID','GITHUB_CLIENT_SECRET','GITHUB_REDIRECT_URI'],
'openai':['OPENAI_API_KEY'],
'smtp':['ROOT404_VERIFY_SMTP_HOST','ROOT404_VERIFY_SMTP_FROM','ROOT404_VERIFY_RECIPIENT'],
'postgres':['ROOT404_VERIFY_DATABASE_URL'], 'redis':['ROOT404_VERIFY_REDIS_URL'],
'nginx_tls':['ROOT404_VERIFY_PUBLIC_URL']}
result={}
for name,keys in checks.items():
    missing=[key for key in keys if not os.environ.get(key)]
    valid=not missing
    if valid and name in {'google','github'}:
        uri=urlsplit(os.environ[keys[-1]])
        valid=uri.scheme=='https' and bool(uri.hostname) and not uri.username and not uri.query and not uri.fragment and uri.path==f'/oauth/callback/{name}'
    result[name]={'status':'CONFIGURED_BUT_UNVERIFIED' if valid else 'BLOCKED','missing_names':missing}
print(json.dumps(result,indent=2))
raise SystemExit(0 if all(row['status']=='CONFIGURED_BUT_UNVERIFIED' for row in result.values()) else 1)
PY
