#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
: "${ROOT404_STACK_ENV:?Private env file outside checkout required}"
: "${ROOT404_BACKUP_FILE:?Absolute custom-format backup filename required}"
[[ "${ROOT404_ALLOW_RESTORE_DRILL:-}" == yes ]] || { echo 'Explicit disposable staging restore consent required'; exit 2; }
[[ "$ROOT404_STACK_ENV" = /* && "$ROOT404_STACK_ENV" != "$ROOT"* && "$ROOT404_BACKUP_FILE" = /* ]] || exit 2
name="root404_restore_$(date -u +%s)_$RANDOM"
compose=(docker compose --env-file "$ROOT404_STACK_ENV")
# Never overwrites or drops an existing DB, even if configured production DB name.
"${compose[@]}" exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" exec createdb -U "$POSTGRES_USER" "$1"' sh "$name"
"${compose[@]}" exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" exec pg_restore --exit-on-error --no-owner -U "$POSTGRES_USER" -d "$1"' sh "$name" < "$ROOT404_BACKUP_FILE"
revision=$("${compose[@]}" exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" exec psql -U "$POSTGRES_USER" -d "$1" -Atc "SELECT version_num FROM alembic_version"' sh "$name")
[[ "$revision" == 0007 ]] || { echo 'FAIL: restored schema revision mismatch'; exit 1; }
printf 'PASS: restored schema0007 into isolated database %s; retained for operator data-integrity checks.\n' "$name"
printf '%s\n' 'Restore is not complete until representative records/constraints are verified. No source database changed.'
