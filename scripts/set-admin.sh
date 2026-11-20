#!/usr/bin/env bash
# Trusted operator-only role provisioning. No account created, no public route.
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
: "${ROOT404_STACK_ENV:?Private staging env file OUTSIDE checkout required}"
: "${ROOT404_ADMIN_EMAIL:?Existing verified target email required privately}"
[[ "$ROOT404_STACK_ENV" = /* && "$ROOT404_STACK_ENV" != "$ROOT"* ]] || exit 2
[[ "${ROOT404_ALLOW_ADMIN_CHANGE:-}" == yes ]] || { echo 'BLOCKED: explicit role change consent required'; exit 2; }
[[ "${ROOT404_ADMIN_ROLE:-}" == grant || "${ROOT404_ADMIN_ROLE:-}" == revoke ]] || exit 2
# -e NAME forwards value from caller environment, never command arguments/logs.
docker compose --env-file "$ROOT404_STACK_ENV" exec -T -e ROOT404_ADMIN_EMAIL -e ROOT404_ADMIN_ROLE -e ROOT404_ALLOW_ADMIN_CHANGE backend python -m app.manage set-admin
