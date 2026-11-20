import pytest
from fastapi import HTTPException
from app.core.database import SessionLocal
from app.models.project import Project
from app.services import judge
from app.services.grading_contracts import ORIGINAL_PROJECTS,original_eligibility


@pytest.mark.parametrize('slug',list(ORIGINAL_PROJECTS))
def test_generic_database_rows_can_never_certify_original_project(monkeypatch,slug):
    with SessionLocal() as db:
        project=db.query(Project).filter_by(slug=slug).one()
        previous=project.test_cases
        project.test_cases=[{'stdin':'','expected_stdout':'FORGED PASS\n'}]
        db.commit()
    monkeypatch.setattr(judge,'_execute',lambda *args:pytest.fail('Original project reached generic executor'))
    try:
        with pytest.raises(HTTPException) as failure:
            judge.run_moulinette(slug,{'main.c':'int main(void){return 0;}'})
        assert failure.value.status_code==503
        assert original_eligibility(slug)['grading_enabled'] is False
    finally:
        with SessionLocal() as db:
            db.query(Project).filter_by(slug=slug).one().test_cases=previous;db.commit()
