from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project, UserProjectProgress
from app.models.submission import Submission
from app.services.judge import run_moulinette
from app.services.skill_graph import SkillGraphService
from app.services.gamification import GamificationService
from app.services.integrity import IntegrityService
import uuid

router = APIRouter(prefix="/projects", tags=["Projects"])

class SubmitRequest(BaseModel):
    files: dict
    language: str = "c"

@router.get("/")
def list_projects(
    status: Optional[str] = None,
    lang: Optional[str] = None,
    q: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = db.query(Project).all()
    
    # Get user progress for each
    progress_map = {}
    progresses = db.query(UserProjectProgress).filter(UserProjectProgress.user_id == current_user.id).all()
    for p in progresses:
        progress_map[p.project_id] = p
    
    result = []
    for proj in projects:
        prog = progress_map.get(proj.id)
        item = {
            "id": proj.id,
            "slug": proj.slug,
            "name": proj.name,
            "level": proj.level,
            "level_value": proj.level_value,
            "lang": proj.lang,
            "langColor": proj.lang_color,
            "desc": proj.description,
            "tags": proj.tags or [],
            "status": prog.status if prog else proj.status_default,
            "progress": prog.progress if prog else None,
            "score": prog.best_score if prog else None,
            "xp": proj.xp,
            "duration": proj.duration,
            "difficulty": proj.difficulty,
            "requires": proj.requires
        }
        # Filters
        if status and status != "all" and item["status"] != status:
            continue
        if lang and lang != "all" and item["lang"] != lang:
            continue
        if q and q.lower() not in f"{item['name']} {item['desc']} {' '.join(item['tags'])}".lower():
            continue
        result.append(item)
    
    # Sort by level
    result.sort(key=lambda x: x["level_value"])
    return result

@router.get("/{slug}")
def get_project(slug: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    progress = db.query(UserProjectProgress).filter(
        UserProjectProgress.user_id == current_user.id,
        UserProjectProgress.project_id == project.id
    ).first()
    
    # Recent submissions
    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.project_id == project.id
    ).order_by(Submission.created_at.desc()).limit(5).all()
    
    return {
        "id": project.id,
        "slug": project.slug,
        "name": project.name,
        "level": project.level,
        "lang": project.lang,
        "langColor": project.lang_color,
        "desc": project.description,
        "long_description": project.long_description,
        "tags": project.tags,
        "xp": project.xp,
        "duration": project.duration,
        "difficulty": project.difficulty,
        "requires": project.requires,
        "objectives": project.objectives or [],
        "constraints": project.constraints or [],
        "status": progress.status if progress else project.status_default,
        "progress": progress.progress if progress else 0,
        "score": progress.best_score if progress else None,
        "attempts": progress.attempts if progress else 0,
        "submissions": [
            {
                "id": s.id,
                "status": s.status,
                "score": s.score,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "tests": s.tests
            } for s in submissions
        ]
    }

@router.post("/{slug}/submit")
def submit_project(
    slug: str,
    payload: SubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    # Check if locked
    progress = db.query(UserProjectProgress).filter(
        UserProjectProgress.user_id == current_user.id,
        UserProjectProgress.project_id == project.id
    ).first()
    
    if progress and progress.status == "locked":
        raise HTTPException(status_code=403, detail="Projet verrouillé, complète les prérequis")
    
    # Run moulinette
    result = run_moulinette(slug, payload.files, payload.language)
    
    # Save submission
    submission = Submission(
        user_id=current_user.id,
        project_id=project.id,
        files=payload.files,
        language=payload.language,
        status="success" if result["score"] >= 80 else "failed",
        score=result["score"],
        tests=result["tests"],
        logs=result["logs"]
    )
    db.add(submission)
    
    # Check plagiarism against recent submissions for same project
    other_subs = db.query(Submission).filter(
        Submission.project_id == project.id,
        Submission.user_id != current_user.id
    ).order_by(Submission.created_at.desc()).limit(20).all()
    
    existing_codes = []
    for s in other_subs:
        if s.files:
            existing_codes.append("".join(s.files.values()))
    
    if existing_codes:
        new_code = "".join(payload.files.values())
        plag = IntegrityService.check_plagiarism(new_code, existing_codes)
        submission.similarity_score = plag["similarity"]
        if plag["is_plagiarism"]:
            submission.integrity_flags = ["high_similarity"]
    
    # Update progress
    if not progress:
        progress = UserProjectProgress(
            user_id=current_user.id,
            project_id=project.id,
            status="progress",
            progress=0
        )
        db.add(progress)
    
    progress.attempts += 1
    progress.progress = max(progress.progress, min(100, result["score"]))
    if result["score"] > progress.best_score:
        progress.best_score = result["score"]
    
    if result["score"] >= 80:
        progress.status = "passed"
        # Unlock next projects
        # Find projects that require this one
        next_projects = db.query(Project).filter(Project.requires == slug).all()
        for np in next_projects:
            np_progress = db.query(UserProjectProgress).filter(
                UserProjectProgress.user_id == current_user.id,
                UserProjectProgress.project_id == np.id
            ).first()
            if not np_progress:
                np_progress = UserProjectProgress(
                    user_id=current_user.id,
                    project_id=np.id,
                    status="available"
                )
                db.add(np_progress)
            elif np_progress.status == "locked":
                np_progress.status = "available"
        
        # Gamification
        gamif = GamificationService.complete_project(current_user, project.xp, result["score"], db)
        # Skill graph
        SkillGraphService.update_from_submission(current_user, submission, project, result["score"], db)
    else:
        progress.status = "progress"
    
    db.commit()
    db.refresh(submission)
    
    # Log audit
    IntegrityService.log_action(
        current_user.id, "project_submit", "project", project.id,
        {"score": result["score"], "slug": slug}, db=db
    )
    
    return {
        "ok": True,
        "submission_id": submission.id,
        "score": result["score"],
        "tests": result["tests"],
        "logs": result["logs"],
        "status": progress.status,
        "progress": progress.progress,
        "xp_earned": project.xp * result["score"] // 100 if result["score"] >= 80 else 0,
        "next_projects_unlocked": [p.slug for p in db.query(Project).filter(Project.requires == slug).all()] if result["score"] >= 80 else []
    }

@router.get("/{slug}/submissions")
def get_submissions(slug: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.slug == slug).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    subs = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.project_id == project.id
    ).order_by(Submission.created_at.desc()).all()
    
    return [
        {
            "id": s.id,
            "status": s.status,
            "score": s.score,
            "tests": s.tests,
            "logs": s.logs,
            "similarity": s.similarity_score,
            "created_at": s.created_at.isoformat() if s.created_at else None
        } for s in subs
    ]

@router.post("/seed")
def seed_projects(db: Session = Depends(get_db)):
    """Seed default projects - for dev only"""
    default_projects = [
        {
            "slug": "get_next_line",
            "name": "get_next_line",
            "description": "Lis une ligne depuis un file descriptor, sans jamais perdre le fil.",
            "level": "Niveau 1",
            "level_value": 1.0,
            "lang": "C",
            "lang_color": "#3B9EFF",
            "tags": ["Solo", "I/O", "Buffer"],
            "xp": 1200,
            "duration": "1 sem.",
            "difficulty": 2,
            "status_default": "done",
            "objectives": ["Gérer plusieurs FD", "Gérer BUFFER_SIZE variable"],
        },
        {
            "slug": "ft_printf",
            "name": "ft_printf",
            "description": "Recode la fonction variadique la plus utilisée de la libc.",
            "level": "Niveau 2",
            "level_value": 2.0,
            "lang": "C",
            "lang_color": "#3B9EFF",
            "tags": ["Solo", "Variadic", "Parsing"],
            "xp": 1500,
            "duration": "2 sem.",
            "difficulty": 3,
            "status_default": "done",
        },
        {
            "slug": "minishell",
            "name": "minishell",
            "description": "Écris ton propre shell : parsing, pipes, redirections, builtins et signaux.",
            "level": "Niveau 4",
            "level_value": 4.0,
            "lang": "C",
            "lang_color": "#3B9EFF",
            "tags": ["Duo", "Unix", "Parsing"],
            "xp": 3200,
            "duration": "4 sem.",
            "difficulty": 5,
            "status_default": "progress",
        },
        {
            "slug": "philosophers",
            "name": "philosophers",
            "description": "Résous le problème des philosophes avec threads et mutex, sans data race.",
            "level": "Niveau 3",
            "level_value": 3.0,
            "lang": "C",
            "lang_color": "#3B9EFF",
            "tags": ["Solo", "Threads", "Concurrence"],
            "xp": 2100,
            "duration": "2 sem.",
            "difficulty": 4,
            "status_default": "available",
        },
        {
            "slug": "netpractice",
            "name": "netpractice",
            "description": "Configure des réseaux TCP/IP et comprends enfin le masque de sous-réseau.",
            "level": "Niveau 4",
            "level_value": 4.2,
            "lang": "Réseau",
            "lang_color": "#2ECC71",
            "tags": ["Solo", "Réseau"],
            "xp": 1100,
            "duration": "3 j.",
            "difficulty": 2,
            "status_default": "done",
        },
        {
            "slug": "cub3d",
            "name": "cub3d",
            "description": "Un moteur de rendu 3D en raycasting, inspiré du légendaire Wolfenstein 3D.",
            "level": "Niveau 5",
            "level_value": 5.0,
            "lang": "C",
            "lang_color": "#3B9EFF",
            "tags": ["Duo", "Graphique", "Maths"],
            "xp": 3600,
            "duration": "4 sem.",
            "difficulty": 5,
            "status_default": "available",
        },
        {
            "slug": "webserv",
            "name": "webserv",
            "description": "Implémente un serveur HTTP/1.1 conforme, non-bloquant, façon NGINX.",
            "level": "Niveau 6",
            "level_value": 6.0,
            "lang": "C++",
            "lang_color": "#F26FA4",
            "tags": ["Trio", "Réseau", "HTTP"],
            "xp": 4200,
            "duration": "5 sem.",
            "difficulty": 5,
            "status_default": "locked",
            "requires": "minishell",
        },
        {
            "slug": "inception",
            "name": "inception",
            "description": "Orchestre une infrastructure multi-conteneurs avec Docker Compose.",
            "level": "Niveau 6",
            "level_value": 6.5,
            "lang": "Docker",
            "lang_color": "#3B9EFF",
            "tags": ["Solo", "DevOps", "Docker"],
            "xp": 2800,
            "duration": "3 sem.",
            "difficulty": 4,
            "status_default": "locked",
            "requires": "webserv",
        },
        {
            "slug": "ft_transcendence",
            "name": "ft_transcendence",
            "description": "Le projet final : une SPA temps réel avec un Pong multijoueur en ligne.",
            "level": "Niveau 8",
            "level_value": 8.0,
            "lang": "Web",
            "lang_color": "#F5B942",
            "tags": ["Groupe", "Fullstack", "WebSocket"],
            "xp": 8000,
            "duration": "8 sem.",
            "difficulty": 5,
            "status_default": "locked",
            "requires": "inception",
        },
    ]
    
    for data in default_projects:
        existing = db.query(Project).filter(Project.slug == data["slug"]).first()
        if not existing:
            p = Project(**data)
            db.add(p)
    db.commit()
    return {"ok": True, "count": len(default_projects)}
