# Account privacy and retention

Implemented endpoints under `/api/account`, all owner-authenticated:
- GET/PUT `/privacy`: portfolio and public directory/ranking opt-in, defaultfalse.
- PUT `/profile`: display name and bio, bounded and rendered as text.
- GET `/export`: own account/owned records only, no password/session secrets or
  other learners' code/messages.16MiB/10000rows-per-table synchronous limits;
  oversize returns413, not a partial success. Operator-assisted private export
  needed beyond that. Response no-store. JSON download available in Settings.
- POST `/sessions/revoke-all`: atomic persistent session epoch; invalidates all
  previous bearer tokens, including the caller. Newly verified OTP uses new epoch.
- DELETE account: exact email confirmation plus recent sign-in (<=10minutes).
  Deletes active database user/code/messages/mentor/progress and owned children;
  shared room/opponent/reviewer references SET NULL; other users remain intact.
  Export also requires recent sign-in. JWT loss is not substituted for deletion.

SQLite API tests and real local PostgreSQL16.2 tests verify selected ownership,
revocation/deletion/cascades. This is not a complete privacy/legal compliance audit.
Directory opt-out controls public search/rankings, not intentional shared-room or
peer interaction identity. Public portfolio excludes email/full-name by default;
users must not put private information in their display name or bio.

## Retention enforcement
Operator-scheduled CLI; never silently delete existing data during startup:
```sh
PYTHONPATH=backend .venv/bin/python -m app.manage retention          # dry-run counts
PYTHONPATH=backend .venv/bin/python -m app.manage retention --apply  # irreversible purge
PYTHONPATH=backend .venv/bin/python -m app.manage cleanup-auth
```
Defaults: mentor questions/advice30days, submission code90days, room messages90days,
audit90days. Override MENTOR_RETENTION_DAYS, SUBMISSION_RETENTION_DAYS,
MESSAGE_RETENTION_DAYS, AUDIT_RETENTION_DAYS (1–3650). Review policy with data owner
before scheduling --apply. Submission deletion cascades associated correction
records; completed progress/awarded XP are preserved. Dry-run/apply tested locally;
no production scheduler or production data purge was run.

Account deletion cannot erase another person's quotations, already-downloaded
exports or external AI provider records. Establish processor terms and deletion
handling with the provider; never promise instant provider/backup erasure. Backups
must be encrypted, access-controlled, time-bounded and restored with an erasure
ledger before service. Backup retention/restore-erasure workflow is still an
operator release gate, not an implemented guarantee.

Questions/advice may contain sensitive source even though review code is not
separately stored in history. Warn users not to submit secrets. SecretFilter
redacts configured secrets, bearer strings, URL credentials and email addresses;
error detail/tracebacks are withheld rather than emitting arbitrary DB/client text.
Do not log request bodies/source/OTP. This filter is defense-in-depth, not a full
DLP guarantee; host/proxy/provider logs need independent review and policies.

In-app notifications are private owner records (migration0005); bounded account
export and account deletion include them. NOTIFICATION_RETENTION_DAYS defaults90;
normal dry-run/apply retention CLI includes expired alerts. It never purges on
startup. Only review booking and final-feedback events currently create alerts;
this is not email/push or comprehensive product-event coverage.
