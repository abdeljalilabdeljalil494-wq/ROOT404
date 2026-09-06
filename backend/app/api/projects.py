"""Projects & Path system.

Endpoints (contract from frontend/src/services/api.js):
    GET  /projects                 → list (per-user status)
    GET  /projects/{slug}          → single project (404 when unknown)
    POST /projects/{slug}/submit   → {ok, id, status, message}
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.db import get_db
from ..core.security import get_current_user
from ..schemas import SubmitIn
from ..services.serializers import project_payload

router = APIRouter()


def _get_project(db: Session, slug: str) -> models.Project:
    q = select(models.Project).where(models.Project.slug == slug)
    project = db.execute(q).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail=f"Projet introuvable : {slug}")
    return project


def _user_project_map(user: models.User) -> dict[str, models.UserProject]:
    return {up.project.id: up for up in user.user_projects}


def _done_slugs(user: models.User) -> set[str]:
    return {up.project.slug for up in user.user_projects if up.status == "done"}


def _payload(db: Session, user: models.User, project: models.Project,
             ups: dict | None = None, done: set | None = None) -> dict:
    ups = ups if ups is not None else _user_project_map(user)
    done = done if done is not None else _done_slugs(user)
    return project_payload(project, ups.get(project.id), done)


@router.get("")
def list_projects(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.execute(
        select(models.Project).order_by(models.Project.order, models.Project.id)
    ).scalars().all()
    ups = _user_project_map(user)
    done = _done_slugs(user)
    return [project_payload(p, ups.get(p.id), done) for p in projects]


@router.get("/{slug}")
def get_project(slug: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _get_project(db, slug)
    return _payload(db, user, project)


@router.post("/{slug}/submit")
def submit_project(
    slug: str,
    body: SubmitIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Store a submission for the Judge / Moulinette (execution engine lands
    in the next roadmap step — submissions are queued as `pending`)."""
    project = _get_project(db, slug)
    files = [f.model_dump() for f in body.files]
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier soumis.")

    # Prerequisite gate
    if project.requires and project.requires not in _done_slugs(user):
        raise HTTPException(
            status_code=400,
            detail=f"Prérequis non validé : termine d'abord « {project.requires} ».",
        )

    ups = _user_project_map(user)
    up = ups.get(project.id)
    if up is None:
        up = models.UserProject(user_id=user.id, project_id=project.id, status="progress", progress=10)
        db.add(up)
    elif up.status == "failed":
        from ..services.serializers import aware, now as _now

        if up.retry_after is not None and aware(up.retry_after) > _now():
            raise HTTPException(
                status_code=409,
                detail="Nouvelle tentative pas encore disponible (pénalité en cours).",
            )
        up.status = "progress"
        up.score = None
        up.retry_after = None
    elif up.status != "done":
        up.status = "progress"

    submission = models.Submission(
        user_id=user.id, project_id=project.id, files=files, status="pending"
    )
    db.add(submission)
    db.add(models.ActivityEvent(
        user_id=user.id, project=project.slug,
        kind="Soumission en attente", score="En cours", tone="brand", xp=0,
    ))
    db.commit()

    return {
        "ok": True,
        "id": submission.id,
        "status": "pending",
        "message": "Soumission enregistrée — la Moulinette analysera ton code (moteur de jugement en construction).",
    }
