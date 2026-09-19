"""ORM models package. Importing this module registers every model on Base."""
from __future__ import annotations

from app.models.project import Project, Submission
from app.models.user import User

__all__ = ["User", "Project", "Submission"]
