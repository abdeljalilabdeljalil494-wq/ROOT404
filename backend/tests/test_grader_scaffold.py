from pathlib import Path
import pytest
from app.services.grading_contracts import ORIGINAL_PROJECTS
from app.services.project_graders import CaseResult, score_cases, require_grader, GraderUnavailable


@pytest.mark.parametrize('slug', list(ORIGINAL_PROJECTS))
def test_original_scaffolds_cannot_enable_execution(slug):
    template=Path(__file__).resolve().parents[2]/'docs'/'subjects'/f'{slug}.md'
    assert 'SUBJECT TEMPLATE (NOT A SPECIFICATION)' in template.read_text()
    with pytest.raises(GraderUnavailable): require_grader(slug)


def test_only_trusted_weighted_cases_form_grade_without_hidden_details():
    grade=score_cases((CaseResult('public',True,1,False),CaseResult('secret',False,3,True)))
    assert grade.score==25 and grade.total==2 and grade.passed==1
    assert 'secret' not in repr(grade)


@pytest.mark.parametrize('cases', [(), (CaseResult('x',True,0,False),),
    (CaseResult('x',True,1,False),CaseResult('x',False,1,True)),
    (CaseResult('x','success',1,False),)])
def test_malformed_or_duplicate_trusted_results_rejected(cases):
    with pytest.raises(ValueError): score_cases(cases)
