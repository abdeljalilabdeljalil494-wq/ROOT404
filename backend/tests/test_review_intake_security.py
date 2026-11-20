"""Independent current-code regressions, not IDs from the unavailable report."""
from pathlib import Path
import re
import pytest
from app.services.judge import validate_files
from executor_service.service import Job


@pytest.mark.parametrize('name',['a//b.py','a/./b.py','a/.hidden.py','a name.py','-main.py'])
def test_backend_rejects_dispatcher_invalid_filenames(name):
    with pytest.raises(ValueError): Job(files={name:'print(0)'},language='python')
    assert validate_files({name:'print(0)'},'python')[0] is False


def test_production_script_csp_disallows_inline_javascript():
    root=Path(__file__).resolve().parents[2]
    dockerfile=(root/'frontend/Dockerfile').read_text()
    policy=re.search(r'add_header Content-Security-Policy "([^"]+)"',dockerfile).group(1)
    scripts=next(part for part in policy.split(';') if part.strip().startswith('script-src'))
    assert "'unsafe-inline'" not in scripts
    assert "'unsafe-eval'" not in scripts


@pytest.mark.parametrize('name',['main.py','src/main.py','a..b.py'])
def test_ordinary_dispatcher_paths_are_not_rejected_as_traversal(name):
    assert Job(files={name:'print(0)'},language='python').files
    assert validate_files({name:'print(0)'},'python')[0] is True
