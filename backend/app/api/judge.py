"""Judge / Moulinette endpoints.

    POST /judge/run               {slug, files?} → {lines, exit, via}
    POST /judge/moulinette/{slug} {files?}       → {tests, score, status, …}

`files` (when given) is the workspace editor content — it is stored as a
real submission and judged immediately. Without `files`, the judge re-runs
the user's latest submission for that project, or the platform template.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.db import get_db
from ..core.security import get_current_user
from ..schemas import SubmitIn
from ..services import moulinette

router = APIRouter()


def _get_project(db: Session, slug: str) -> models.Project:
    q = select(models.Project).where(models.Project.slug == slug)
    project = db.execute(q).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail=f"Projet introuvable : {slug}")
    return project


def _files_from(body: SubmitIn | None) -> list | None:
    if body is None or not body.files:
        return None
    return [f.model_dump() for f in body.files]


@router.post("/run")
def judge_run(body: SubmitIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Workspace « Exécuter »: compile + one run, terminal lines back."""
    files = _files_from(body)
    if files is None:
        files = [
            {"path": t["name"], "content": t["content"]}
            for t in moulinette.get_template(body.slug)["files"]
        ]
    return moulinette.run_quick(files, body.slug)


def _latest_submission_files(db: Session, user: models.User, project: models.Project):
    q = (
        select(models.Submission)
        .where(models.Submission.user_id == user.id, models.Submission.project_id == project.id)
        .order_by(models.Submission.created_at.desc())
        .limit(1)
    )
    sub = db.execute(q).scalar_one_or_none()
    return sub.files if sub is not None and sub.files else None


@router.post("/moulinette/{slug}")
def judge_moulinette(
    slug: str,
    body: SubmitIn | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = _get_project(db, slug)
    files = _files_from(body)
    if files is None:
        files = _latest_submission_files(db, user, project)
    if files is None:
        files = [
            {"path": t["name"], "content": t["content"]}
            for t in moulinette.get_template(slug)["files"]
        ]
    return moulinette.run_judge(db, user, project, files)
