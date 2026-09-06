"""The Moulinette — judge engine.

Pipeline per run:
  1. isolated workdir (sandbox.fresh_workdir)
  2. write the submitted (or template) files
  3. compile step — gate: `make` if a Makefile exists, else
     `gcc -Wall -Wextra -Werror -o app …` (auto -pthread/-lm).
     Student code without `main()` is compiled against the hidden
     per-project harness (get_next_line, ft_printf).
  4. test rows (per-project suite, or generic) — each row: status
     pass / warn / skip / fail + short detail, weighted score.
  5. persist on the Submission + apply progression (XP / level).

Score: earned/total points × 100. `skip` (e.g. valgrind absent) counts
as neutral. A run PASSES at score >= PASS_SCORE with no failed row.
"""

import json
import math
import os
import re
import time

from sqlalchemy import select

from .. import models
from . import sandbox, templates
from .progress import PASS_SCORE, apply_judge_result, recompute_level

MAIN_RE = re.compile(r"\bint\s+main\s*\(")
C_SRC_RE = re.compile(r"\.(c|h)$", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Templates (what the workspace shows per project) & hidden harnesses
# ---------------------------------------------------------------------------

TEMPLATES = {
    "get_next_line": {"file": "get_next_line.c", "lang": "c", "code": templates.GET_NEXT_LINE_C},
    "ft_printf": {"file": "ft_printf.c", "lang": "c", "code": templates.FT_PRINTF_C},
    "philosophers": {"file": "philosophers.c", "lang": "c", "code": templates.PHILOSOPHERS_C},
    "minishell": {"file": "minishell.c", "lang": "c", "code": templates.MINISHELL_C},
    "netpractice": {"file": "main.c", "lang": "c", "code": templates.MAIN_GENERIC_C},
    "cub3d": {"file": "main.c", "lang": "c", "code": templates.MAIN_GENERIC_C},
    "webserv": {"file": "main.cpp", "lang": "c++", "code": None},  # C++: no sample yet → generic C
    "inception": {"file": "main.c", "lang": "c", "code": templates.MAIN_GENERIC_C},
    "ft_transcendence": {"file": "main.c", "lang": "c", "code": templates.MAIN_GENERIC_C},
}
# webserv template uses the generic C skeleton until a C++ sample lands
TEMPLATES["webserv"]["code"] = templates.MAIN_GENERIC_C
TEMPLATES["webserv"]["file"] = "main.c"
TEMPLATES["webserv"]["lang"] = "c"

HARNESS = {
    "get_next_line": {"file": "gnl_test_main.c", "code": templates.GNL_HARNESS_C},
    "ft_printf": {"file": "ft_printf_test_main.c", "code": templates.FT_PRINTF_HARNESS_C},
}

# How `POST /judge/run` (workspace « Exécuter ») executes the binary
RUN_ARGS = {
    "philosophers": (["5", "10"], None),
    "minishell": ([], "echo hello ROOT 404\n"),
}


def get_template(slug: str) -> dict:
    t = TEMPLATES.get(slug) or TEMPLATES["netpractice"]
    return {"slug": slug, "files": [{"name": t["file"], "lang": t["lang"], "content": t["code"]}]}


# ---------------------------------------------------------------------------
# Test suites (rows shown in the UI)
# ---------------------------------------------------------------------------

def _suite_gnl():
    return [
        {"name": "Compilation (gcc -Wall -Wextra -Werror)", "kind": "compile", "points": 100},
        {"name": "Lignes standard (abc, def, ghi)", "kind": "run", "args": [], "stdin": None,
         "expect": {"op": "contains", "value": "T1 OK"}, "points": 100},
        {"name": "Fin de fichier (NULL après EOF)", "kind": "run", "args": [], "stdin": None,
         "expect": {"op": "contains", "value": "T2 OK"}, "points": 100},
        {"name": "Norme (analyse statique)", "kind": "norm", "points": 100},
        {"name": "Fuites mémoire (valgrind)", "kind": "leaks", "points": 100},
    ]


def _suite_printf():
    return [
        {"name": "Compilation (gcc -Wall -Wextra -Werror)", "kind": "compile", "points": 100},
        {"name": "Conversions %d / %s / %c", "kind": "run", "args": [], "stdin": None,
         "expect": {"op": "contains", "value": "T1: 42 root404 X"}, "points": 100},
        {"name": "Pourcentage échappé (%%)", "kind": "run", "args": [], "stdin": None,
         "expect": {"op": "contains", "value": "T2: -17% ok"}, "points": 100},
        {"name": "Norme (analyse statique)", "kind": "norm", "points": 100},
        {"name": "Fuites mémoire (valgrind)", "kind": "leaks", "points": 100},
    ]


def _suite_philo():
    return [
        {"name": "Compilation (gcc -Wall -Wextra -Werror -pthread)", "kind": "compile", "points": 100},
        {"name": "5 philosophes × 10 itérations (exit 0)", "kind": "run", "args": ["5", "10"], "stdin": None,
         "expect": {"op": "exit", "value": 0}, "points": 100},
        {"name": "Cycle think / eat / sleep", "kind": "run", "args": ["3", "2"], "stdin": None,
         "expect": {"op": "contains", "value": "is eating"}, "points": 100},
        {"name": "Norme (analyse statique)", "kind": "norm", "points": 100},
        {"name": "Fuites mémoire (valgrind)", "kind": "leaks", "points": 100},
    ]


def _suite_minishell():
    return [
        {"name": "Compilation (gcc -Wall -Wextra -Werror)", "kind": "compile", "points": 100},
        {"name": "Builtin echo", "kind": "run", "args": [], "stdin": "echo hello ROOT 404\n",
         "expect": {"op": "contains", "value": "hello ROOT 404"}, "points": 100},
        {"name": "Commande externe (ls)", "kind": "run", "args": [], "stdin": "ls -1\n",
         "expect": {"op": "contains", "value": "app"}, "points": 100},
        {"name": "Commande inconnue (erreur gérée)", "kind": "run", "args": [],
         "stdin": "definitely_nosuch_cmd_xyz\n", "expect": {"op": "stderr_contains", "value": "command not found"},
         "points": 100},
        {"name": "Norme (analyse statique)", "kind": "norm", "points": 100},
        {"name": "Fuites mémoire (valgrind)", "kind": "leaks", "points": 100},
    ]


def _suite_generic():
    return [
        {"name": "Compilation (gcc -Wall -Wextra -Werror)", "kind": "compile", "points": 100},
        {"name": "Exécution (exit 0, sortie non vide)", "kind": "run", "args": [], "stdin": None,
         "expect": {"op": "exit_and_output", "value": 0}, "points": 100},
        {"name": "Norme (analyse statique)", "kind": "norm", "points": 100},
    ]


SUITES = {
    "get_next_line": _suite_gnl,
    "ft_printf": _suite_printf,
    "philosophers": _suite_philo,
    "minishell": _suite_minishell,
}

# ---------------------------------------------------------------------------
# Norm (light static analysis — full norminette integration is a later step)
# ---------------------------------------------------------------------------

def norm_check(files: list) -> tuple[bool, str]:
    issues = []
    n_files = 0
    for f in files:
        if not C_SRC_RE.search(f["path"]):
            continue
        n_files += 1
        lines = f["content"].splitlines()
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"{os.path.basename(f['path'])} L{i}: ligne > 120 caractères")
            if line != line.rstrip():
                issues.append(f"{os.path.basename(f['path'])} L{i}: espaces en fin de ligne")
            if i == len(lines) and line != "" and not f["content"].endswith("\n"):
                issues.append(f"{os.path.basename(f['path'])}: pas de fin de ligne")
    if issues:
        return False, issues[0]
    if n_files == 0:
        return True, "aucun fichier C"
    return True, f"{n_files} fichier(s) OK"


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------

def _write_files(workdir: str, files: list) -> None:
    for f in files:
        path = os.path.join(workdir, os.path.basename(f["path"]))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(f["content"])


def _compile(workdir: str, slug: str, files: list) -> tuple[bool, str]:
    """Returns (ok, terminal_lines_text)."""
    sources = [f for f in files if f["path"].endswith(".c")]
    harness = HARNESS.get(slug)
    has_main = any(MAIN_RE.search(f["content"]) for f in sources)
    if not has_main:
        if harness is None:
            return False, "erreur: aucun main() et pas de harness — projet incomplet."
        with open(os.path.join(workdir, harness["file"]), "w") as fh:
            fh.write(harness["code"])
        # The harness #includes the student source(s); drop those from the
        # compile list to avoid multiple-definition link errors.
        included = set(re.findall(r'#include\s+"([^"]+\.c)"', harness["code"]))
        sources = [
            f for f in sources
            if os.path.basename(f["path"]) not in included
        ]
        sources = sources + [{"path": harness["file"], "content": harness["code"]}]

    inc_dirs = sorted({os.path.dirname(f["path"]) for f in files if os.path.dirname(f["path"])})
    inc_flags = [f"-I{os.path.join(workdir, d)}" for d in inc_dirs] + [f"-I{workdir}"]

    if os.path.exists(os.path.join(workdir, "Makefile")):
        cmd = ["make", "-j4"]
    else:
        cmd = ["gcc", "-Wall", "-Wextra", "-Werror", "-o", "app",
               "-pthread", "-lm"] + inc_flags + [os.path.basename(s["path"]) for s in sources]
    return _exec_step(workdir, cmd)


def _exec_step(workdir: str, cmd: list, stdin: str | None = None) -> tuple[bool, str]:
    t0 = time.time()
    r = sandbox.run_command(workdir, cmd, stdin=stdin, timeout=sandbox.LIMIT_TIMEOUT)
    dt = time.time() - t0
    lines = []
    if r.stdout:
        lines.append(r.stdout.rstrip("\n"))
    if r.stderr:
        lines.append(r.stderr.rstrip("\n"))
    if not lines:
        lines.append("(aucune sortie)" if r.ok else "(aucune erreur capturée)")
    lines.append(f"↳ exit {r.exit_code} · {dt:.2f}s · {r.via}")
    return (r.ok, "\n".join(lines))


def _run_row(workdir: str, slug: str, spec: dict, files: list) -> tuple[str, str]:
    kind = spec["kind"]
    if kind == "norm":
        ok, detail = norm_check(files)
        return ("pass" if ok else "fail"), detail
    if kind == "leaks":
        import shutil

        have_valgrind = sandbox.docker_available() or shutil.which("valgrind") is not None
        if not have_valgrind:
            return "skip", "valgrind absent — sauté"
        args, stdin = RUN_ARGS.get(slug, ([], None))
        if slug == "philosophers":
            args = ["3", "2"]
        ok, out = _exec_step(workdir, ["valgrind", "--leak-check=full", "--error-exitcode=99", "./app"] + args, stdin=stdin)
        if ok:
            m = re.search(r"definitely lost: (\d+) bytes", out)
            lost = int(m.group(1)) if m else 0
            if lost == 0:
                return "pass", "0 bytes lost"
            return "fail", f"{lost} bytes lost"
        if "not found" in out:
            return "skip", "valgrind absent — sauté"
        return "fail", out.splitlines()[-1][:60]
    # kind == "run"
    ok, out = _exec_step(workdir, ["./app"] + spec.get("args", []), stdin=spec.get("stdin"))
    exp = spec["expect"]
    out_full = out
    head, _, _ = out.partition("\n")
    exit_txt = re.search(r"exit (-?\d+)", out_full)
    exit_code = int(exit_txt.group(1)) if exit_txt else (0 if ok else 1)
    op = exp["op"]
    if op == "contains":
        if exp["value"] in out_full:
            return "pass", "OK"
        return "fail", "sortie inattendue"
    if op == "stderr_contains":
        if exp["value"] in out_full:
            return "pass", "OK"
        return "fail", "erreur inattendue"
    if op == "exit":
        if exit_code == exp["value"]:
            return "pass", f"exit {exit_code}"
        return "fail", f"exit {exit_code} ≠ {exp['value']}"
    if op == "exit_and_output":
        body = out_full.split("\n")[0] if out_full else ""
        if exit_code == exp["value"] and body and "aucune sortie" not in body:
            return "pass", f"exit {exit_code}"
        return "fail", f"exit {exit_code}, sortie vide"
    return "fail", "test invalide"


def _terminal_lines(compile_out: str, run_out: str | None) -> list:
    lines = [{"t": "cmd", "v": "$ gcc -Wall -Wextra -Werror -o app …"}]
    for l in compile_out.split("\n"):
        lines.append({"t": "ok" if l.startswith("↳") else "out", "v": l})
    if run_out is not None:
        lines.append({"t": "cmd", "v": "$ ./app"})
        for l in run_out.split("\n"):
            lines.append({"t": "ok" if l.startswith("↳") else "out", "v": l})
    return lines


def run_judge(db, user, project, files: list, submission: models.Submission | None = None):
    """Full moulinette run. Persists on `submission` (or creates one).
    Returns the JSON payload {tests, score, status, submission_id, lines, via}."""
    slug = project.slug
    suite = SUITES.get(slug, _suite_generic)()

    workdir = sandbox.fresh_workdir(f"{slug}_{user.id[-8:]}")
    _write_files(workdir, files)

    via = "docker" if sandbox.docker_available() else "local"
    compile_ok, compile_out = _compile(workdir, slug, files)

    tests = []
    earned = 0
    total = 0
    for spec in suite:
        total += spec["points"]
        if spec["kind"] == "compile":
            if compile_ok:
                tests.append({"name": spec["name"], "status": "pass", "detail": "OK"})
                earned += spec["points"]
            else:
                tail = (compile_out or "erreur de compilation").strip().splitlines()[-1]
                tests.append({"name": spec["name"], "status": "fail",
                              "detail": f"erreur de compilation — {tail[:140]}"})
            continue
        if not compile_ok:
            tests.append({"name": spec["name"], "status": "fail", "detail": "non testé (compilation)"})
            continue
        status, detail = _run_row(workdir, slug, spec, files)
        tests.append({"name": spec["name"], "status": status, "detail": detail})
        if status in ("pass", "skip"):
            earned += spec["points"]
        elif status == "warn":
            earned += spec["points"] // 2

    score = int(math.floor(100 * earned / total)) if total else 0
    has_fail = any(t["status"] == "fail" for t in tests)
    passed = score >= PASS_SCORE and not has_fail and compile_ok
    status = "passed" if passed else "failed"

    if submission is None:
        submission = models.Submission(user_id=user.id, project_id=project.id, files=files, status="pending")
        db.add(submission)
        db.flush()
    submission.status = status
    submission.score = score
    submission.tests = tests
    submission.terminal = _terminal_lines(compile_out, None)
    submission.via = via
    db.flush()

    # Progression (XP / level / activity) — idempotent per project.
    up = db.execute(
        select(models.UserProject).where(
            models.UserProject.user_id == user.id,
            models.UserProject.project_id == project.id,
        )
    ).scalar_one_or_none()
    apply_judge_result(db, user, project, up, score, passed)
    if passed:
        recompute_level(user)
    db.commit()

    return {
        "tests": tests,
        "score": score,
        "status": status,
        "passed": passed,
        "error": None if compile_ok else (compile_out or "erreur de compilation"),
        "submission_id": submission.id,
        "via": via,
        "lines": submission.terminal,
    }


def run_quick(workdir_files: list, slug: str) -> dict:
    """`POST /judge/run` — compile + one run, returns terminal lines only."""
    workdir = sandbox.fresh_workdir(f"run_{slug}")
    _write_files(workdir, workdir_files)
    compile_ok, compile_out = _compile(workdir, slug, workdir_files)
    run_out = None
    if compile_ok:
        args, stdin = RUN_ARGS.get(slug, ([], None))
        if slug == "philosophers":
            args = ["3", "2"]
        run_ok, run_out = _exec_step(workdir, ["./app"] + args, stdin=stdin)
    lines = _terminal_lines(compile_out, run_out)
    exit_txt = re.search(r"exit (-?\d+)", (run_out or compile_out).splitlines()[-1]) if (run_out or compile_out) else None
    return {"lines": lines, "exit": int(exit_txt.group(1)) if exit_txt else None,
            "via": "docker" if sandbox.docker_available() else "local"}
