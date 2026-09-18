"""
Moulinette / Judge Engine — Polyglot Execution Engine
Simulates Docker sandbox execution for development.
When JUDGE_ENABLED=True, would call real Docker.
"""
import time
import random
import hashlib
from typing import Dict, List, Tuple
from app.core.config import settings

# Test templates per project type
MOULINETTE_TEMPLATES = {
    "c": [
        {"name": "Norminette", "weight": 15},
        {"name": "Makefile (rules & flags)", "weight": 10},
        {"name": "Fuites mémoire (valgrind)", "weight": 20},
        {"name": "Compilation -Wall -Wextra -Werror", "weight": 15},
        {"name": "Tests fonctionnels", "weight": 30},
        {"name": "Cas limites", "weight": 10},
    ],
    "default": [
        {"name": "Norme / Style", "weight": 20},
        {"name": "Compilation / Execution", "weight": 25},
        {"name": "Tests fonctionnels", "weight": 35},
        {"name": "Cas limites", "weight": 10},
        {"name": "Performance", "weight": 10},
    ]
}

PROJECT_TESTS = {
    "get_next_line": [
        {"name": "Norminette", "detail": "OK"},
        {"name": "Makefile", "detail": "OK"},
        {"name": "Fuites mémoire", "detail": "0 bytes lost"},
        {"name": "Lecture simple", "detail": "OK"},
        {"name": "Multi FD", "detail": "OK"},
        {"name": "BUFFER_SIZE variable", "detail": "OK"},
    ],
    "ft_printf": [
        {"name": "Norminette", "detail": "OK"},
        {"name": "Makefile", "detail": "OK"},
        {"name": "Fuites mémoire", "detail": "0 bytes lost"},
        {"name": "Conversions cspdiuxX%", "detail": "OK"},
        {"name": "Flags et largeur", "detail": "OK"},
        {"name": "Cas limites", "detail": "OK"},
    ],
    "minishell": [
        {"name": "Norminette", "detail": "OK"},
        {"name": "Makefile (rules & flags)", "detail": "OK"},
        {"name": "Fuites mémoire (valgrind)", "detail": "0 bytes lost"},
        {"name": "Builtins (echo, cd, pwd, env)", "detail": "OK"},
        {"name": "Pipes & redirections", "detail": "38/38"},
        {"name": "Heredoc multi-niveaux", "detail": "2 cas limites"},
        {"name": "Signaux (SIGINT / SIGQUIT)", "detail": "Ctrl-\\ non géré"},
    ],
    "philosophers": [
        {"name": "Norminette", "detail": "OK"},
        {"name": "Data races (thread sanitizer)", "detail": "OK"},
        {"name": "Deadlock detection", "detail": "OK"},
        {"name": "5 philosophes / 800ms", "detail": "OK"},
        {"name": "1 philosophe", "detail": "doit mourir"},
        {"name": "Fuites mémoire", "detail": "OK"},
    ]
}

def _hash_code(files: Dict[str, str]) -> str:
    combined = "".join(sorted(files.values()))
    return hashlib.sha256(combined.encode()).hexdigest()[:12]

def simulate_execution(files: Dict[str, str], language: str = "c") -> Tuple[int, List[dict], str]:
    """
    Simulate code execution in isolated container.
    Returns score, tests, logs
    """
    code_hash = _hash_code(files)
    random.seed(code_hash)  # Deterministic for same code
    
    # Simulate execution time
    exec_time = random.uniform(0.5, 3.5)
    time.sleep(min(exec_time * 0.1, 0.5))  # Small delay to simulate work
    
    # Check for obvious failure patterns
    all_code = "".join(files.values()).lower()
    has_main = "main" in all_code or "def " in all_code or "function" in all_code
    is_empty = len(all_code.strip()) < 20
    
    if is_empty:
        tests = [
            {"name": "Fichiers présents", "status": "fail", "detail": "Aucun code détecté"},
            {"name": "Compilation", "status": "fail", "detail": "Échec"},
        ]
        return 0, tests, "Erreur: aucun code soumis"
    
    # Select template
    template = PROJECT_TESTS.get("minishell")  # default, will be overridden by project slug
    # Generate results with some randomness but mostly passing for non-empty code
    
    tests = []
    passed = 0
    for t in template:
        # 85% chance to pass for decent code
        r = random.random()
        if "main" in all_code or len(all_code) > 200:
            # More code = higher chance to pass
            if r < 0.85:
                status = "pass"
                passed += 1
            elif r < 0.93:
                status = "warn"
            else:
                status = "fail"
        else:
            if r < 0.6:
                status = "pass"
                passed += 1
            elif r < 0.8:
                status = "warn"
            else:
                status = "fail"
        tests.append({
            "name": t["name"],
            "status": status,
            "detail": t["detail"] if status == "pass" else ("2 cas limites" if status == "warn" else "Échec")
        })
    
    score = int((passed / len(tests)) * 100) if tests else 0
    # Bonus for code quality heuristics
    if "malloc" in all_code and "free" in all_code:
        score = min(100, score + 5)
    
    logs = f"""$ cc -Wall -Wextra -Werror -Iincludes -c src/*.c
$ cc obj/*.o -lreadline -o minishell
$ ./minishell < test_cases.txt
Tests: {passed}/{len(tests)} passed
Score: {score}/100
Execution time: {exec_time:.2f}s
Container: ubuntu:22.04 (isolated, no network)
Memory limit: 512MB | CPU: 1 vCPU
"""
    return score, tests, logs

def run_moulinette(project_slug: str, files: Dict[str, str], language: str = "c") -> dict:
    """
    Main entry point for Moulinette
    """
    # Use project-specific template if available
    global PROJECT_TESTS
    template = PROJECT_TESTS.get(project_slug, PROJECT_TESTS["minishell"])
    
    code_hash = _hash_code(files)
    random.seed(code_hash + project_slug)
    
    all_code = "".join(files.values())
    is_empty = len(all_code.strip()) < 10
    
    if is_empty:
        return {
            "project_slug": project_slug,
            "score": 0,
            "tests": [{"name": "Soumission", "status": "fail", "detail": "Vide"}],
            "passed": 0,
            "total": 1,
            "logs": "Aucun fichier soumis",
            "execution_time": 0.1
        }
    
    tests = []
    passed = 0
    for t in template:
        r = random.random()
        # Heuristic: longer code has better chance
        bonus = min(0.2, len(all_code) / 5000)
        if r < (0.75 + bonus):
            status = "pass"
            passed += 1
            detail = t["detail"]
        elif r < 0.88:
            status = "warn"
            detail = "2 cas limites"
        else:
            status = "fail"
            detail = "Échec"
            if "Signal" in t["name"]:
                detail = "Ctrl-\\ non géré"
        tests.append({"name": t["name"], "status": status, "detail": detail})
    
    score = int((passed / len(template)) * 100)
    logs = f"""=== ROOT 404 Moulinette v2.1 ===
Project: {project_slug}
Language: {language}
Container: ubuntu:22.04 (id: {code_hash})
Isolation: network=none, cpu=1, memory=512m

$ norminette {project_slug}/
OK

$ make -j4
cc -Wall -Wextra -Werror ...

$ valgrind --leak-check=full ./test_runner
=={random.randint(1000,9999)}== 0 bytes lost

Result: {passed}/{len(template)} | Score: {score}/100
"""
    return {
        "project_slug": project_slug,
        "score": score,
        "tests": tests,
        "passed": passed,
        "total": len(template),
        "logs": logs,
        "execution_time": random.uniform(0.8, 4.2)
    }

def run_code_in_sandbox(code: str, language: str, test_input: str = "") -> dict:
    """
    Polyglot runner - simulates execution
    In production would spawn Docker container with runner_*.py
    """
    start = time.time()
    
    # Security checks
    forbidden = ["os.system", "subprocess", "socket", "import os", "__import__", "eval(", "exec("]
    if language == "python" and any(f in code for f in forbidden):
        return {
            "status": "security_violation",
            "output": "",
            "error": "Forbidden pattern detected - network/process access denied in sandbox",
            "execution_time": 0
        }
    
    # Simulate execution
    time.sleep(0.2)
    elapsed = time.time() - start
    
    return {
        "status": "success",
        "output": f"Execution simulated for {language}\nInput: {test_input[:100]}\nOutput: Hello ROOT 404",
        "error": "",
        "execution_time": elapsed
    }

class JudgeService:
    @staticmethod
    def check_plagiarism(code1: str, code2: str) -> float:
        """Simple AST-like similarity check"""
        # Normalize
        def normalize(c):
            return ''.join(c.lower().split())
        n1, n2 = normalize(code1), normalize(code2)
        if not n1 or not n2:
            return 0.0
        # Simple Jaccard on bigrams
        def bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))
        b1, b2 = bigrams(n1), bigrams(n2)
        if not b1 or not b2:
            return 0.0
        intersection = len(b1 & b2)
        union = len(b1 | b2)
        return (intersection / union * 100) if union else 0.0

    @staticmethod
    def analyze_complexity(code: str) -> dict:
        lines = code.split('\n')
        return {
            "loc": len([l for l in lines if l.strip()]),
            "functions": code.count("def ") + code.count("function ") + code.count("int ") // 2,
            "complexity": min(10, code.count("if") + code.count("for") + code.count("while")),
            "has_comments": "//" in code or "#" in code or "/*" in code
        }
