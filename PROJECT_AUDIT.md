# ROOT404 repository audit — 2026-11-18

## Verdict
**Not production ready; the full completion mission is not satisfied.** This is an
existing React/FastAPI platform with useful models, routers and branded UI, but a
large portion of its original user experience was a prototype. Historical
`FINAL_REPORT.md` and `PROJECT_STATUS.md` claims are not acceptance evidence.

## Method and scope
- Enumerated all source directories, frontend pages/components, backend routers,
  services, SQLAlchemy models, schemas, tests, Dockerfiles, Compose and env examples.
- `docs/SOURCE_INVENTORY.md` records 144 source/test files and static flags. This is
  a static inventory, not a claim of manual runtime verification of every screen.
- Inspected the root .env without disclosure: whitespace only; no live credentials
  identified there. Historical Git objects/external secret stores were not audited.
- Installed original declared Python requirements in a virtual environment and
  frontend dependencies via npm ci before evaluating failures.
- Baseline reproduced: 53 backend tests, 14 frontend tests, frontend build passed.
  Lint failed because ESLint was not declared. Existing frontend tests mostly
  checked independent strings/localStorage, not imported production service code.

## Original findings
| Area | Finding |
|---|---|
| UI integration | Most pages import fixture data directly; service mock mode defaulted ON, with silent network fallback in development. |
| Authentication | Login/register screens used timers, not auth API. Backend created OTPs without delivering email. Development last-OTP fallback allowed replay/expiry/attempt-limit bypass. OTP/rate state was process-local. Logout did not revoke tokens. |
| Judge | Backend produced hash-seeded scores, fictional Valgrind/container/security logs. C runner also simulated compilation. CLI fallback fabricated results. Backend was not connected to an executor. |
| Database | Substantial FK/index/check-constraint coverage exists. Alembic dependency but no migration history. Production startup called create_all and could seed a fake user/progress. PostgreSQL driver missing. |
| Gamification | Server XP existed, but repeat successful project submissions could repeatedly award XP; helper commits fragmented submission transactions. |
| Access control | Public catalog/room/Piscine seed writes; room messages readable/writable without membership; peer review repeat awards. |
| Analytics | Dashboard activity/weekly/heatmaps and learning metrics invented values even for new users. Arena rankings/wins and exam scores fabricated. |
| Infrastructure | Default DB/Redis passwords; judge unconfined seccomp/AppArmor; internal bridge inaccurately described as absolute isolation. Frontend builder omitted Vite devDependency, hid build errors. Backend COPY referenced a user before creation. |
| Dependencies | Initial/current-old trees contained known vulnerable packages. Audited upgrades and JWT-library replacement were necessary. |
| Performance | N+1 queries in room/portfolio/review/coalition paths, incomplete pagination, in-process general throttles, synchronous HTTP/SQL request work. |
| Integrations | SMTP missing; AI templates stood in for a provider; Redis config did not establish application use; no real-time room implementation. |

## Implemented remediation
See `BUGS_AND_FIXES.md`, `ENGINEERING_REPORT.md`, and tests. Core auth/dashboard/
projects/workspace now use APIs and truthful unavailable states. Other student
prototype screens remain available only with explicit development demo selection;
that restriction is **not** completion of those features. Public marketing carries
a development/illustrative-data disclosure.

## Remaining engineering, not merely external blockers
A per-job executor service/orchestrator, production project suites, persistent exam/
hiring/mentorship workflows, conversation history, all gated frontend integrations,
moderation/notifications/realtime, comprehensive pagination/performance work,
accessibility/responsive/browser E2E and a broader access-control review remain.
