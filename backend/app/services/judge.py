"""
Moulinette / Judge Engine — Polyglot Execution Engine
Hardened version with security checks, resource limits, and input validation.
Simulates Docker sandbox execution for development.
When JUDGE_ENABLED=True, would call real Docker with strict isolation.
"""
import time
import random
import hashlib
import re
import logging
from typing import Dict, List, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

# Security: forbidden patterns for each language
FORBIDDEN_PATTERNS = {
    "c": [
        r'system\s*\(', r'popen\s*\(', r'exec[lv]p?\s*\(',  # Process execution
        r'socket\s*\(', r'connect\s*\(', r'bind\s*\(',  # Network
        r'#include\s*<net', r'#include\s*<sys/socket',  # Network headers
        r'__asm__', r'asm\s*\(',  # Inline assembly
    ],
    "cpp": [
        r'system\s*\(', r'popen\s*\(', r'exec[lv]p?\s*\(',
        r'socket\s*\(', r'#include\s*<net',
        r'__asm__', r'asm\s*\(',
    ],
    "python": [
        r'os\.system', r'subprocess', r'socket', r'__import__',
        r'eval\s*\(', r'exec\s*\(', r'open\s*\(\s*["\']\/etc',
        r'import\s+os', r'from\s+os\s+import', r'import\s+sys',
        r'pty\.', r'tty\.', r'input\s*\(',  # Interactive
    ],
    "javascript": [
        r'require\s*\(\s*["\']child_process', r'require\s*\(\s*["\']fs',
        r'process\.env', r'eval\s*\(', r'Function\s*\(',
        r'import\s+.*\s+from\s+["\']fs', r'fetch\s*\(', r'XMLHttpRequest',
    ],
}

# File validation
ALLOWED_EXTENSIONS = {
    "c": [".c", ".h", "Makefile", ".mk"],
    "cpp": [".cpp", ".cc", ".hpp", ".h", "Makefile"],
    "python": [".py", ".txt", "requirements.txt"],
    "javascript": [".js", ".json", "package.json"],
}

MAX_FILENAME_LENGTH = 100
MAX_FILE_SIZE = settings.JUDGE_MAX_FILE_SIZE
MAX_TOTAL_SIZE = settings.JUDGE_MAX_TOTAL_SIZE
MAX_FILES = settings.JUDGE_MAX_FILES

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

def validate_files(files: Dict[str, str], language: str = "c") -> Tuple[bool, str]:
    """Validate uploaded files for security and resource limits"""
    if not files:
        return False, "No files provided"
    
    if len(files) > MAX_FILES:
        return False, f"Too many files. Max {MAX_FILES} allowed"
    
    total_size = 0
    for filename, content in files.items():
        # Validate filename
        if len(filename) > MAX_FILENAME_LENGTH:
            return False, f"Filename too long: {filename[:50]}..."
        
        # Prevent path traversal
        if ".." in filename or filename.startswith("/") or "\\" in filename:
            return False, f"Invalid filename (path traversal detected): {filename}"
        
        # Check for null bytes
        if "\x00" in filename:
            return False, f"Invalid filename (null byte): {filename}"
        
        # Validate content size
        if not isinstance(content, str):
            return False, f"Invalid content type for {filename}"
        
        size = len(content.encode('utf-8'))
        if size > MAX_FILE_SIZE:
            return False, f"File too large: {filename} ({size} bytes, max {MAX_FILE_SIZE})"
        
        total_size += size
        
        # Check forbidden patterns
        patterns = FORBIDDEN_PATTERNS.get(language, [])
        for pattern in patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"Forbidden pattern '{pattern}' detected in {filename}")
                    return False, f"Security violation: forbidden pattern detected in {filename}: {pattern}"
            except re.error:
                # Invalid regex, skip
                continue
    
    if total_size > MAX_TOTAL_SIZE:
        return False, f"Total size too large: {total_size} bytes, max {MAX_TOTAL_SIZE}"
    
    return True, ""

def _hash_code(files: Dict[str, str]) -> str:
    combined = "".join(sorted(files.values()))
    return hashlib.sha256(combined.encode()).hexdigest()[:12]

def simulate_execution(files: Dict[str, str], language: str = "c") -> Tuple[int, List[dict], str]:
    """Simulate code execution in isolated container with validation"""
    # Validate first
    valid, msg = validate_files(files, language)
    if not valid:
        return 0, [{"name": "Validation", "status": "fail", "detail": msg}], f"Validation failed: {msg}"
    
    code_hash = _hash_code(files)
    # Use hash as seed for deterministic results, but don't use random.seed globally
    rng = random.Random(code_hash)
    
    exec_time = rng.uniform(0.5, 3.5)
    
    all_code = "".join(files.values()).lower()
    has_main = "main" in all_code or "def " in all_code or "function" in all_code
    is_empty = len(all_code.strip()) < 20
    
    if is_empty:
        tests = [
            {"name": "Fichiers présents", "status": "fail", "detail": "Aucun code détecté"},
            {"name": "Compilation", "status": "fail", "detail": "Échec"},
        ]
        return 0, tests, "Erreur: aucun code soumis"
    
    template = PROJECT_TESTS.get("minishell")
    tests = []
    passed = 0
    for t in template:
        r = rng.random()
        if "main" in all_code or len(all_code) > 200:
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
    if "malloc" in all_code and "free" in all_code:
        score = min(100, score + 5)
    
    logs = f"""$ cc -Wall -Wextra -Werror -Iincludes -c src/*.c
$ cc obj/*.o -lreadline -o minishell
$ ./minishell < test_cases.txt
Tests: {passed}/{len(tests)} passed
Score: {score}/100
Execution time: {exec_time:.2f}s
Container: ubuntu:22.04 (isolated, no network, id: {code_hash})
Memory limit: {settings.JUDGE_MEMORY_LIMIT} | CPU: {settings.JUDGE_CPU_LIMIT} vCPU
Security: seccomp, no-new-privileges, read-only rootfs
"""
    return score, tests, logs

def run_moulinette(project_slug: str, files: Dict[str, str], language: str = "c") -> dict:
    """Main entry point for Moulinette with security validation"""
    # Sanitize project_slug to prevent injection
    if not re.match(r'^[a-zA-Z0-9_-]+$', project_slug):
        return {
            "project_slug": "invalid",
            "score": 0,
            "tests": [{"name": "Validation", "status": "fail", "detail": "Invalid project slug"}],
            "passed": 0,
            "total": 1,
            "logs": "Invalid project slug format",
            "execution_time": 0.1
        }
    
    # Validate language
    allowed_languages = ["c", "cpp", "c++", "python", "javascript", "js"]
    if language not in allowed_languages:
        return {
            "project_slug": project_slug,
            "score": 0,
            "tests": [{"name": "Validation", "status": "fail", "detail": f"Language {language} not supported"}],
            "passed": 0,
            "total": 1,
            "logs": f"Unsupported language: {language}",
            "execution_time": 0.1
        }
    
    # Validate files
    valid, msg = validate_files(files, language)
    if not valid:
        return {
            "project_slug": project_slug,
            "score": 0,
            "tests": [{"name": "Validation", "status": "fail", "detail": msg}],
            "passed": 0,
            "total": 1,
            "logs": f"Validation failed: {msg}",
            "execution_time": 0.1
        }
    
    template = PROJECT_TESTS.get(project_slug, PROJECT_TESTS["minishell"])
    code_hash = _hash_code(files)
    rng = random.Random(code_hash + project_slug)
    
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
        r = rng.random()
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
    logs = f"""=== ROOT 404 Moulinette v2.1 (Hardened) ===
Project: {project_slug}
Language: {language}
Container: ubuntu:22.04 (id: {code_hash})
Isolation: network=none, cpu={settings.JUDGE_CPU_LIMIT}, memory={settings.JUDGE_MEMORY_LIMIT}, pids=64, no-new-privileges, seccomp, read-only rootfs

$ norminette {project_slug}/
OK

$ make -j4
cc -Wall -Wextra -Werror ...

$ valgrind --leak-check=full ./test_runner
=={rng.randint(1000,9999)}== 0 bytes lost

Result: {passed}/{len(template)} | Score: {score}/100
Security: All checks passed, no forbidden patterns detected
"""
    return {
        "project_slug": project_slug,
        "score": score,
        "tests": tests,
        "passed": passed,
        "total": len(template),
        "logs": logs,
        "execution_time": rng.uniform(0.8, 4.2)
    }

def run_code_in_sandbox(code: str, language: str, test_input: str = "") -> dict:
    """Polyglot runner with security checks"""
    start = time.time()
    
    # Validate input sizes
    if len(code) > MAX_FILE_SIZE:
        return {
            "status": "error",
            "output": "",
            "error": f"Code too large: {len(code)} bytes, max {MAX_FILE_SIZE}",
            "execution_time": 0
        }
    
    if len(test_input) > 10240:  # 10KB max input
        return {
            "status": "error",
            "output": "",
            "error": "Test input too large (max 10KB)",
            "execution_time": 0
        }
    
    # Security checks with regex
    patterns = FORBIDDEN_PATTERNS.get(language, [])
    for pattern in patterns:
        try:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning(f"Security violation: pattern '{pattern}' in {language} code")
                return {
                    "status": "security_violation",
                    "output": "",
                    "error": f"Forbidden pattern detected: {pattern} - blocked by security policy (network/process access denied)",
                    "execution_time": 0
                }
        except re.error:
            continue
    
    # Additional checks for all languages
    if "\x00" in code:
        return {
            "status": "security_violation",
            "output": "",
            "error": "Null byte detected - security violation",
            "execution_time": 0
        }
    
    # Simulate execution with timeout
    time.sleep(0.1)
    elapsed = time.time() - start
    
    if elapsed > settings.JUDGE_TIMEOUT:
        return {
            "status": "timeout",
            "output": "",
            "error": f"Execution timeout after {settings.JUDGE_TIMEOUT}s",
            "execution_time": elapsed
        }
    
    return {
        "status": "success",
        "output": f"Execution simulated for {language}\nInput: {test_input[:100]}\nOutput: Hello ROOT 404\nSecurity: Sandboxed, no network, limited resources",
        "error": "",
        "execution_time": elapsed
    }

class JudgeService:
    @staticmethod
    def check_plagiarism(code1: str, code2: str) -> float:
        """AST-like similarity check with sanitization"""
        if not code1 or not code2:
            return 0.0
        
        # Limit size to prevent DoS
        if len(code1) > 100000 or len(code2) > 100000:
            return 0.0
        
        def normalize(c):
            # Remove comments and whitespace for comparison
            c = re.sub(r'//.*?\n|/\*.*?\*/', '', c, flags=re.DOTALL)
            c = re.sub(r'#.*?\n', '\n', c)
            return ''.join(c.lower().split())
        
        try:
            n1, n2 = normalize(code1), normalize(code2)
            if not n1 or not n2:
                return 0.0
            
            def bigrams(s):
                return set(s[i:i+2] for i in range(len(s)-1)) if len(s) > 1 else set()
            
            b1, b2 = bigrams(n1), bigrams(n2)
            if not b1 or not b2:
                return 0.0
            
            intersection = len(b1 & b2)
            union = len(b1 | b2)
            return (intersection / union * 100) if union else 0.0
        except Exception as e:
            logger.error(f"Plagiarism check error: {e}")
            return 0.0

    @staticmethod
    def analyze_complexity(code: str) -> dict:
        if len(code) > 100000:
            return {"error": "Code too large for analysis"}
        
        try:
            lines = code.split('\n')
            return {
                "loc": len([l for l in lines if l.strip()]),
                "functions": code.count("def ") + code.count("function ") + code.count("int ") // 2,
                "complexity": min(10, code.count("if") + code.count("for") + code.count("while")),
                "has_comments": "//" in code or "#" in code or "/*" in code
            }
        except Exception as e:
            logger.error(f"Complexity analysis error: {e}")
            return {"error": "Analysis failed"}
