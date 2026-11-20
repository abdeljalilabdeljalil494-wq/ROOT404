# Original project grading completion matrix

Status: **INCOMPLETE — original catalog cannot be certified for grading.**
Source inventory: `backend/app/api/projects.py:seed_projects`, mirrored original
frontend catalog. Foundation exercises are separate projects and never substitute
for these requirements. No original project has actual isolated grading evidence.
An explicit eligibility registry hard-fails503 for every original project BEFORE generic execution, even if DB test rows exist; no points are awarded. No existing project/data was removed.

| Original project | Languages/artifacts | Matching suite/hidden cases | Compilation/runtime validation | Required edge/acceptance cases | Actual execution evidence | Status / remaining limitations |
|---|---|---|---|---|---|---|
| get_next_line | C function/library; FD input | None | Generic C compiler only; no project harness | EOF/empty/no final newline/long lines/BUFFER_SIZE variants/multiple FDs/read errors/ownership/leaks | None for this project | INCOMPLETE: versioned ABI, allowed functions, compile flags/headers and project-specific harness missing |
| ft_printf | C variadic library | None | No linked oracle/harness | Required conversions, width/precision if assigned, NULL/pointer, signed limits, return counts, write errors/leaks | None | INCOMPLETE: exact conversion/bonus contract, libc oracle exclusions and harness missing |
| minishell | C POSIX process tree | None | Generic single-main compilation does not validate shell | Quoting/expansion/exit status/pipes/redirections/heredoc/builtins/signals/FD leaks | None | INCOMPLETE: subject/version/build contract and PTY/process-tree harness missing; source regex bans currently reject legitimate exec operations and must be replaced by project-aware policy |
| philosophers | C threads/processes depending on subject | None | No concurrency/sanitizer/time oracle |1philosopher/starvation/death timing/meal bounds/no deadlock/data races/argument errors/cleanup | None | INCOMPLETE: versioned CLI/time tolerances, concurrency/TSAN harness missing |
| netpractice | Network topology/configuration artifact | None | C/stdio execution is NOT a valid grader | IP/subnet/gateway/routes/connectivity/invalid masks/topology constraints | None | INCOMPLETE: exercise topology/schema and deterministic network model/oracle absent; do not run arbitrary host network setup |
| cub3d | C graphics/raycasting + map/assets | None | No graphics/build harness | Map validation/closed boundaries/textures/colors/player states/render/control/leaks | None | INCOMPLETE: subject/asset format/graphics dependencies and headless rendering oracle missing |
| webserv | C++ HTTP server/config artifacts | None | No protocol/server harness | HTTP parsing/limits/methods/status/CGI/timeouts/partial I/O/concurrency/path traversal | None | INCOMPLETE: protocol/CGI/config requirements and loopback-only isolated client/server harness missing; never enable external job networking |
| inception | Compose/build/config artifacts | None | Ordinary code executor is intentionally insufficient | Service dependency/TLS/volumes/restart/secrets/non-root/network boundaries | None | INCOMPLETE: infrastructure rubric and separate nested-infrastructure review worker needed; NEVER give learner containers Docker socket or privileged mode |
| ft_transcendence | Full-stack Web/SPA/realtime artifacts | None | No app/browser/multiplayer harness | Auth/authorization/game states/reconnect/input validation/privacy/concurrency/accessibility | None | INCOMPLETE: exact chosen modules/API/DB/game contracts and disposable multi-service/browser harness missing |

## Implemented foundation curriculum (not original-project completion)
| Project | Language | Suite and hidden API behavior | Compile/runtime/edges | Execution evidence | Classification |
|---|---|---|---|---|---|
| foundations-sum-c | C | Versioned10stdin/stdout cases; expected outputs not returned by public API | Real correct/wrong/empty/whitespace/EOF/signed64-bit/boundaries | Trusted GCC process; no real container yet | VERIFIED locally; isolated grading IMPLEMENTED BUT UNVERIFIED |
| foundations-sum-cpp | C++ | Same explicitly defined stream-sum contract | Real G++ reference/wrong programs | Trusted G++ only | VERIFIED locally; isolated grading IMPLEMENTED BUT UNVERIFIED |
| foundations-sum-python | Python | Same contract | Real reference/wrong programs | Trusted Python only | VERIFIED locally; isolated grading IMPLEMENTED BUT UNVERIFIED |
| foundations-sum-javascript | JavaScript | Same contract | Real reference/wrong programs | Trusted Node only | VERIFIED locally; isolated grading IMPLEMENTED BUT UNVERIFIED |

Source: `backend/app/services/project_suites.py`; references:
`judge_sandbox/tests/solutions/`; tests: `backend/tests/test_project_suites.py`.
Generic runner tests separately verify C/C++ compilation failures, Python/JS runtime
errors, four-language infinite-loop termination, output and allocation limits.
They do NOT prove any original project passes. Fixed source cases are inspectable
in this repository; “hidden” means server expectations are not disclosed via API,
not that a public repository is a secret test bank.

## Completion rule
Before enabling an original project, version its actual subject/ABI/artifact and
mandatory/bonus rubric; implement that specific trusted harness; run correct and
adversarial/wrong submissions with the real approved isolated service; verify hidden
case non-disclosure, exact reward/idempotency behavior and grading reproducibility.
Never attach the generic stream-sum suite or award a full project pass from a few
smoke cases. Missing authoritative contracts and missing harness implementation are
explicit blockers, not permission to invent a weaker assignment.

## Current inspected evidence and enforcement
`backend/app/services/grading_contracts.py` records only catalog facts, not invented
subjects. Repository search found no authoritative versioned subjects/spec assets.
`backend/tests/test_original_grading_gate.py` verifies all nine generic-suite bypass
attempts return503 without invoking execution. `scripts/check_project_grading.py`
is read-only and returns exit1/INCOMPLETE: specification BLOCKED, harness INCOMPLETE,
execution BLOCKED and grading_enabled=false for all nine. These are eligibility
contracts, NOT project grading execution evidence. Candidate edge cases above are
review checklists, not authoritative acceptance specifications. Need approved subject
version/mandatory+bonus scope, permitted functions/toolchains/artifacts and rubric;
engineering must then build/review actual trusted harnesses and demonstrate public,
hidden, boundary, invalid-input, compile/runtime and scoring tests per project.

## Private-beta subject intake and harness structure
All nine `docs/subjects/<project>.md` templates now distinguish actual catalog facts
from the precise missing owner inputs and engineering adapter checklist. No complete
authoritative original subject was found; therefore no original grader is claimed
implemented. `project_graders` supplies a typed trusted adapter/reference/result
boundary and tested weighted reducer, with an EMPTY explicit implementation registry.
No dynamic plugin loading or Markdown-driven activation. Existing hard503 gate is
unchanged. Foundation Stream Sum has its own supplied executable spec and tests;
it is not an original-project implementation.

## Next round reinspection
Rechecked tracked READMEs/project definitions and docs/subjects: all nine files
remain explicitly unapproved intake templates, not executable specifications.
No new authoritative original statements/ABIs/rubrics were found. No original
adapter registered/graded; nine hard503 regressions and template tests retained.
Daily mission uses ONLY separately specified foundation Stream Sum Python, never
substitutes for these originals. Read-only inventory remains INCOMPLETE/exit1.
