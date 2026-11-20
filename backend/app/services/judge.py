"""Judge service client and server-owned executable test evaluation. No simulation."""
import time
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
        r'import\s+os', r'from\s+os\s+import',
        r'pty\.', r'tty\.',
    ],
    "javascript": [
        r'require\s*\(\s*["\']child_process',
        r'process\.env', r'eval\s*\(', r'Function\s*\(',
        r'fetch\s*\(', r'XMLHttpRequest',
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

def validate_files(files: Dict[str, str], language: str = "c") -> Tuple[bool, str]:
    """Validate uploaded files for security and resource limits"""
    language = {"py": "python", "js": "javascript", "c++": "cpp"}.get(language.lower(), language.lower())
    if not files:
        return False, "No files provided"

    if len(files) > MAX_FILES:
        return False, f"Too many files. Max {MAX_FILES} allowed"

    if not any(isinstance(content, str) and content.strip() for content in files.values()):
        return False, "Empty code submission"
    total_size = 0
    for filename, content in files.items():
        # Same ASCII/segment grammar as the dispatcher and minimal launcher.
        # Isolation remains the primary control; source regexes are defense only.
        if (not isinstance(filename,str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]{0,99}',filename)
                or any(part in {'','.','..'} or part.startswith('.') for part in filename.split('/'))):
            return False, "Invalid source filename"

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

def _execute(files: Dict[str, str], language: str, test_input: str = "") -> dict:
    """Authenticated service boundary. Never runs submitted code in the API process.

    Deployment must supply a separately audited, per-job isolated executor. The
    repository CLI runner alone is NOT such a service.
    """
    import httpx
    from fastapi import HTTPException
    from pydantic import BaseModel, Field, ValidationError
    from typing import Literal

    from app.core.judge_protocol import verify
    import uuid, time, json

    valid, message = validate_files(files, language)
    if not valid:
        raise HTTPException(status_code=400, detail=message)
    if not settings.JUDGE_ENABLED or not settings.JUDGE_URL.startswith("https://") or len(settings.JUDGE_SHARED_SECRET) < 48 or not settings.JUDGE_EXPECTED_IMAGE:
        raise HTTPException(status_code=503, detail="Isolated code executor is not configured")
    identity=uuid.uuid4().hex
    payload={"files":files,"language":language,"stdin":test_input,
             "timeout_seconds":settings.JUDGE_TIMEOUT,"output_limit_bytes":65536}
    try:
        import ssl
        context = ssl.create_default_context(cafile=settings.JUDGE_CA_FILE or None)
        with httpx.Client(verify=context, timeout=httpx.Timeout(connect=5, read=2 * settings.JUDGE_TIMEOUT + 40, write=10, pool=5), follow_redirects=False, trust_env=False) as client:
            with client.stream("POST", settings.JUDGE_URL.rstrip("/") + "/v2/execute",
                headers={"Authorization": f"Bearer {settings.JUDGE_SHARED_SECRET}",
                         "X-Root404-Request-ID":identity,"X-Root404-Request-Time":str(int(time.time()))},
                json=payload) as response:
                response.raise_for_status()
                body = bytearray()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > 262144:
                        raise ValueError("Oversized executor response")
                return verify(settings.JUDGE_SHARED_SECRET,identity,payload,json.loads(body),expected_image=settings.JUDGE_EXPECTED_IMAGE)
    except (httpx.HTTPError, ValidationError, ValueError):
        logger.warning("Executor unavailable or returned an invalid result")
        raise HTTPException(status_code=503, detail="Isolated code executor unavailable")


def run_moulinette(project_slug: str, files: Dict[str, str], language: str = "c") -> dict:
    from fastapi import HTTPException
    from app.core.database import SessionLocal
    from app.models.project import Project
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", project_slug):
        raise HTTPException(status_code=400, detail="Invalid project slug")
    from app.services.grading_contracts import original_eligibility
    if original_eligibility(project_slug) is not None:
        raise HTTPException(503,'Original project-specific harness and approved contract are not configured')
    with SessionLocal() as db:
        project = db.query(Project).filter_by(slug=project_slug).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        cases = project.test_cases
        allowed_languages = (project.norm_rules or {}).get("allowed_languages")
        canonical_language = {"c++": "cpp", "py": "python", "js": "javascript"}.get(language, language)
        if allowed_languages and canonical_language not in allowed_languages:
            raise HTTPException(status_code=400, detail="Language is not allowed for this project suite")
    if not cases:
        raise HTTPException(status_code=503, detail="Executable test suite not configured for this project")
    if len(cases) > 100 or any(not isinstance(case, dict) or
        not isinstance(case.get("stdin", ""), str) or not isinstance(case.get("expected_stdout"), str) or
        len(case.get("stdin", "").encode()) > 10240 or
        len(case.get("expected_stdout", "").encode()) > 65536 for case in cases):
        raise HTTPException(status_code=503, detail="Invalid project test suite configuration")
    tests = []
    grading_started = time.monotonic()
    elapsed = 0.0
    for index, case in enumerate(cases):
        if time.monotonic() - grading_started > 120:
            raise HTTPException(status_code=503, detail="Project grading deadline exceeded; no grade awarded")
        result = _execute(files, language, case.get("stdin", ""))
        passed = result["status"] == "success" and result["exit_code"] == 0 and result["output"].replace("\r\n", "\n").rstrip("\n") == case["expected_stdout"].replace("\r\n", "\n").rstrip("\n")
        # Do not return hidden inputs, expected outputs, or program output.
        tests.append({"name": f"Test {index + 1}", "status": "pass" if passed else "fail",
                      "detail": "OK" if passed else result["status"] if result["status"] != "success" else "Wrong answer"})
        elapsed += result["execution_time"]
    passed = sum(test["status"] == "pass" for test in tests)
    return {"project_slug": project_slug, "score": passed * 100 // len(tests), "tests": tests,
            "passed": passed, "total": len(tests), "execution_time": elapsed,
            "logs": f"Executed {len(tests)} test cases; {passed} passed."}


def run_code_in_sandbox(code: str, language: str, test_input: str = "") -> dict:
    from fastapi import HTTPException
    extensions = {"c": "c", "cpp": "cpp", "c++": "cpp", "python": "py", "py": "py", "javascript": "js", "js": "js"}
    if language not in extensions or len(code.encode()) > MAX_FILE_SIZE or len(test_input) > 10240:
        raise HTTPException(status_code=400, detail="Invalid code execution request")
    return _execute({f"main.{extensions[language]}": code}, language, test_input)

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
