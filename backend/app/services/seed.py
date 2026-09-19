"""Idempotent startup seeding of the demo project catalogue.

Safe to run on every boot: rows are matched by their unique ``slug`` and only
inserted when missing, so restarts never duplicate data. Concurrent boots are
handled by the unique constraint + IntegrityError fallback.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Project

logger = logging.getLogger(__name__)

#: README Phase 1 demo catalogue (42-style project names).
SEED_PROJECTS = (
    {
        "slug": "libft",
        "title": "Libft — votre première bibliothèque",
        "description": (
            "Recoder un sous-ensemble de la libc (strlen, memcpy, strduplicates, "
            "listes chaînées…) et comprendre la gestion de la mémoire en C."
        ),
        "difficulty": "easy",
        "xp_reward": 100,
    },
    {
        "slug": "ft_printf",
        "title": "ft_printf — formatage sans variadic excuses",
        "description": (
            "Réimplémenter printf(3) avec va_arg: %s %d %x %p, buffers, et "
            "passes par la moulinette sans fuites mémoire."
        ),
        "difficulty": "medium",
        "xp_reward": 150,
    },
    {
        "slug": "minishell",
        "title": "Minishell — un shell POSIX minimal",
        "description": (
            "Parsing lex/yacc, pipes, redirections, signaux, builtins et "
            "gestion de processus — le projet qui séparait les gens à 42."
        ),
        "difficulty": "hard",
        "xp_reward": 300,
    },
)


def seed_projects(db: Session) -> int:
    """Insert missing seed projects. Returns the number of rows created."""
    created = 0
    for spec in SEED_PROJECTS:
        exists = db.scalar(select(Project).where(Project.slug == spec["slug"]))
        if exists is not None:
            continue
        db.add(Project(**spec))
        try:
            db.commit()
            created += 1
        except IntegrityError:  # concurrent boot inserted it first
            db.rollback()
    logger.info("Seed complete: %d project(s) created", created)
    return created
