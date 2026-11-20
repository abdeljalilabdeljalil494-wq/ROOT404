#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
: "${ROOT404_STACK_ENV:?Set private env file outside checkout}"
: "${ROOT404_BACKUP_DIR:?Set approved private backup directory outside checkout}"
[[ "$ROOT404_STACK_ENV" = /* && "$ROOT404_BACKUP_DIR" = /* && "$ROOT404_BACKUP_DIR" != "$ROOT"* && "$ROOT404_STACK_ENV" != "$ROOT"* ]] || { echo 'Use absolute private paths outside checkout'; exit 2; }
umask 077
mkdir -p "$ROOT404_BACKUP_DIR"
file="$ROOT404_BACKUP_DIR/root404-$(date -u +%Y%m%dT%H%M%S)-$RANDOM.dump"
trap '[[ -f "$file" ]] && [[ ! -s "$file" ]] && rm -f "$file"' ERR
# Secrets expand inside the container only, not command arguments or report output.
docker compose --env-file "$ROOT404_STACK_ENV" exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$file"
docker compose --env-file "$ROOT404_STACK_ENV" exec -T db pg_restore --list < "$file" >/dev/null
printf '%s\n' 'PASS: custom-format database backup created and archive catalog checked.' 'IMPORTANT: archive is sensitive, unencrypted; encrypt/store per operator policy. A restore drill is still required.'
# Print only basename; no private directory or database credentials.
basename "$file"
