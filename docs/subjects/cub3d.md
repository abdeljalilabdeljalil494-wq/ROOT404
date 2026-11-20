# cub3d — SUBJECT TEMPLATE (NOT A SPECIFICATION)

Status: BLOCKED subject / INCOMPLETE harness / grading disabled.

## Repository evidence
- Source: `backend/app/api/projects.py:seed_projects`, mirrored frontend catalog.
- Language/artifact label: C.
- Existing description/objectives: Raycasting graphics is described; map/assets/graphics-library contract absent.
- No authoritative versioned statement or acceptance fixtures found in tracked
  project definitions, READMEs or docs. Descriptions and candidate test checklists
  are insufficient to determine a grading contract.

## Owner must provide (leave unapproved until complete)
- [ ] Authorized statement/file or approved location, owner and redistribution policy.
- [ ] Exact version/date, mandatory/bonus scope and selected modules.
- [ ] Deliverable filenames, public ABI/API/CLI/artifact schema and build commands.
- [ ] Allowed functions/libraries/toolchain versions and forbidden behavior.
- [ ] Expected outputs/exit codes/errors; approved oracle and normalization rules.
- [ ] Boundary/invalid inputs, resource constraints and timing/numeric tolerances.
- [ ] Public examples with expected results; confidential hidden fixtures via an
      approved private channel, never a public repository.
- [ ] Scoring weights, mandatory-failure/bonus rules, pass threshold, resubmission policy.
- [ ] Project-specific details: Map/texture/color/asset formats; allowed graphics library/version; controls; deterministic render fixtures and comparison tolerances.

## Engineering adapter checklist (not owner coding work)
- [ ] Record approved subject version and content SHA256 in SubjectReference.
- [ ] Implement trusted adapter conforming to project_graders.TrustedGrader.
- [ ] Keep expected outputs/weights/scoring outside learner containers.
- [ ] Exercise public/hidden/boundary/invalid/compile-error/runtime-error/scoring cases.
- [ ] Prove sandbox receipt verification and prevent learner diagnostics/result forgery.
- [ ] Independently review harness, authz, cleanup and project-appropriate isolation.
- [ ] Record actual execution evidence in PROJECT_GRADING_MATRIX.md.

Filling this template does NOT register or enable a grader. No automatic plugin
imports, no execution of supplied Markdown, no generic stdin/stdout fallback.
