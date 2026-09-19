"""Project catalogue + submission flow (README Phase 1 scope).

Authorization rules:
    * Reading projects: public (only published ones are listed).
    * Creating/reading submissions: authenticated; a user only ever sees
      their own submissions (404 for anyone else's — no existence leak).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Project, Submission, User
from app.schemas import ProjectRead, SubmissionCreate, SubmissionRead

router = APIRouter(tags=["projects"])


def _get_published_project(db: Session, slug: str) -> Project:
    project = db.scalar(select(Project).where(Project.slug == slug))
    if project is None or not project.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found."
        )
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    return list(db.scalars(select(Project).where(Project.is_published.is_(True))))


@router.get("/projects/{slug}", response_model=ProjectRead)
def get_project(slug: str, db: Session = Depends(get_db)) -> Project:
    return _get_published_project(db, slug)


@router.post(
    "/projects/{slug}/submissions",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    slug: str,
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Submission:
    project = _get_published_project(db, slug)

    #: One attempt row per (project, user); a re-submission replaces the code
    #: and returns the row to "pending" for the (future) moulinette run.
    submission = db.scalar(
        select(Submission).where(
            Submission.project_id == project.id, Submission.user_id == current_user.id
        )
    )
    if submission is None:
        submission = Submission(project_id=project.id, user_id=current_user.id)
        db.add(submission)
    submission.language = payload.language
    submission.code = payload.code
    submission.status = "pending"
    submission.score = None
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/submissions/mine", response_model=list[SubmissionRead])
def list_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Submission]:
    return list(
        db.scalars(
            select(Submission)
            .where(Submission.user_id == current_user.id)
            .order_by(Submission.created_at.desc())
        )
    )


@router.get("/submissions/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Submission:
    submission = db.get(Submission, submission_id)
    #: 404 (not 403) for other users' submissions: same signal, no existence leak.
    if submission is None or submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found."
        )
    return submission
