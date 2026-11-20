"""Real trusted execution validates foundation suites, not container isolation."""
from pathlib import Path
import sys
import tempfile
import pytest
from app.core.database import SessionLocal
from app.services.project_suites import seed_execution_projects, sum_suite, LANGUAGES
from app.models.project import Project
from app.services.judge import validate_files
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'judge_sandbox'))
from runners.common import execute


@pytest.mark.parametrize('language,filename', [('c','main.c'), ('cpp','main.cpp'), ('python','main.py'), ('javascript','main.js')])
def test_real_reference_and_incorrect_solutions(language, filename):
    source = (Path(__file__).resolve().parents[2]/'judge_sandbox/tests/solutions'/filename).read_text()
    assert validate_files({filename: source}, language)[0]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/filename
        path.write_text(source)
        for case in sum_suite():
            result = execute(directory, language, case['stdin'])
            assert result['status'] == 'success', result
            assert result['output'] == case['expected_stdout']
        wrong = {'c': '#include <stdio.h>\nint main(void){puts("0");return 0;}',
                 'cpp': '#include <iostream>\nint main(){std::cout<<"0\\n";}',
                 'python': 'print(0)', 'javascript': 'console.log(0)'}[language]
        path.write_text(wrong)
        result = execute(directory, language, '42\n')
        assert result['status'] == 'success' and result['output'] != '42\n'


def test_catalog_seed_is_idempotent_and_preserves_advanced_projects():
    with SessionLocal() as db:
        before = db.query(Project).filter_by(slug='minishell').one().test_cases
        seed_execution_projects(db); seed_execution_projects(db)
        assert db.query(Project).filter(Project.slug.like('foundations-sum-%')).count() == len(LANGUAGES)
        assert db.query(Project).filter_by(slug='minishell').one().test_cases == before
        assert all('expected_stdout' in case for case in sum_suite())
