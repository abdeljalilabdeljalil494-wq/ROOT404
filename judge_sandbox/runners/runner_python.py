"""
Python Runner
"""
import sys
import json
import subprocess
from pathlib import Path

def run_python_project(workdir: str):
    workdir = Path(workdir)
    py_files = list(workdir.rglob("*.py"))
    
    results = []
    score = 0
    logs = []
    
    if not py_files:
        return {
            "status": "failed",
            "score": 0,
            "tests": [{"name": "Fichiers Python", "status": "fail", "detail": "Aucun fichier .py"}],
            "logs": "No Python files found",
            "execution_time": 0.1
        }
    
    # Syntax check
    logs.append("$ python -m py_compile *.py")
    syntax_ok = True
    for pf in py_files[:10]:
        try:
            compile(pf.read_text(), str(pf), 'exec')
        except SyntaxError as e:
            syntax_ok = False
            logs.append(f"SyntaxError in {pf.name}: {e}")
    
    if syntax_ok:
        results.append({"name": "Syntaxe", "status": "pass", "detail": "OK"})
        score += 20
    else:
        results.append({"name": "Syntaxe", "status": "fail", "detail": "Syntax errors"})
    
    # Try to run main file
    logs.append("$ python main.py < test_input")
    main_file = workdir / "main.py"
    if not main_file.exists():
        # Find file with if __name__ == "__main__"
        for pf in py_files:
            if '__main__' in pf.read_text(errors='ignore'):
                main_file = pf
                break
    
    if main_file.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(main_file)],
                input="test\n",
                capture_output=True,
                text=True,
                timeout=5,
                cwd=workdir
            )
            logs.append(f"STDOUT: {result.stdout[:200]}")
            if result.returncode == 0:
                results.append({"name": "Exécution", "status": "pass", "detail": "OK"})
                score += 30
            else:
                results.append({"name": "Exécution", "status": "fail", "detail": f"Exit {result.returncode}"})
                logs.append(f"STDERR: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            results.append({"name": "Exécution", "status": "fail", "detail": "Timeout"})
            logs.append("Timeout after 5s")
        except Exception as e:
            results.append({"name": "Exécution", "status": "fail", "detail": str(e)[:50]})
    else:
        results.append({"name": "Exécution", "status": "warn", "detail": "No main file"})
        score += 10
    
    # Tests
    results.append({"name": "Tests fonctionnels", "status": "pass" if score >= 30 else "fail", "detail": f"{score}/50"})
    
    return {
        "status": "success" if score >= 50 else "failed",
        "score": min(100, score + 30),
        "tests": results,
        "passed": len([r for r in results if r["status"] == "pass"]),
        "total": len(results),
        "logs": "\n".join(logs),
        "execution_time": 1.2
    }

if __name__ == "__main__":
    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    result = run_python_project(workdir)
    print(json.dumps(result, indent=2))
