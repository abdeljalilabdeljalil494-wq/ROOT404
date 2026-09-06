"""Projects & Path system.

Endpoints (contract from frontend/src/services/api.js):
    GET  /projects                 → list (per-user status)
    GET  /projects/{slug}          → single project (404 when unknown)
    POST /projects/{slug}/submit   → {ok, id, status, message}
                                     (the Judge runs in the background)
    GET  /projects/{slug}/template   → platform sample code for the workspace
    GET  /projects/{slug}/last-result → latest judge result (or 404)
"""

import threading

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.db import SessionLocal, get_db
from ..core.security import get_current_user
from ..schemas import SubmitIn
from ..services import moulinette
from ..services.serializers import aware, project_payload, user_payload

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
        user_id=user.id, project_id=project.id, files=files, status="running"
    )
    db.add(submission)
    db.add(models.ActivityEvent(
        user_id=user.id, project=project.slug,
        kind="Soumission en attente", score="En cours", tone="brand", xp=0,
    ))
    db.commit()
    db.refresh(submission)

    # Judge in the background (own session — the request returns immediately).
    threading.Thread(
        target=_judge_background,
        args=(user.id, project.id, submission.id),
        daemon=True,
    ).start()

    return {
        "ok": True,
        "id": submission.id,
        "status": "running",
        "message": "Soumission enregistrée — la Moulinette analyse ton code.",
    }


def _judge_background(user_id: str, project_id: str, submission_id: str) -> None:
    """Worker: run the Moulinette on the stored submission (own DB session)."""
    db = SessionLocal()
    try:
        user = db.get(models.User, user_id)
        project = db.get(models.Project, project_id)
        submission = db.get(models.Submission, submission_id)
        if user is None or project is None or submission is None:
            return
        if not submission.files:
            submission.files = [
                {"path": t["name"], "content": t["content"]}
                for t in moulinette.get_template(project.slug)["files"]
            ]
        moulinette.run_judge(db, user, project, submission.files, submission=submission)
    except Exception:
        import logging

        logging.getLogger("root404.judge").exception("background judge failed")
        try:
            sub = db.get(models.Submission, submission_id)
            if sub is not None and sub.status not in ("passed", "failed"):
                sub.status = "failed"
                sub.score = 0
                sub.tests = [{"name": "Sandbox", "status": "fail", "detail": "erreur interne du juge"}]
                db.commit()
        except Exception:
            db.rollback()
    finally:
        db.close()


@router.get("/{slug}/template")
def get_template(slug: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_project(db, slug)  # 404 when unknown
    return moulinette.get_template(slug)


@router.get("/{slug}/last-result")
def last_result(slug: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = _get_project(db, slug)
    q = (
        select(models.Submission)
        .where(models.Submission.user_id == user.id, models.Submission.project_id == project.id)
        .order_by(models.Submission.created_at.desc())
        .limit(1)
    )
    sub = db.execute(q).scalar_one_or_none()
    if sub is None or not sub.tests:
        raise HTTPException(status_code=404, detail="Aucune soumission jugée pour ce projet.")
    created = aware(sub.created_at)
    return {
        "id": sub.id,
        "status": sub.status,
        "score": sub.score,
        "tests": sub.tests,
        "terminal": sub.terminal,
        "via": sub.via,
        "at": created.isoformat() if created else None,
    }
