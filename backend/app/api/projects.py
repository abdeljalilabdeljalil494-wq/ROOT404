from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, judge_rate_limit
from app.core.security import sanitize_input
from app.core.config import settings
from app.models.user import User
from app.models.project import Project, UserProjectProgress
from app.models.submission import Submission
from app.services.judge import run_moulinette, validate_files
from app.services.skill_graph import SkillGraphService
from app.services.gamification import GamificationService
from app.services.integrity import IntegrityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])

class SubmitRequest(BaseModel):
    files: dict = Field(..., description="Map of filename to content")
    language: str = Field("c", max_length=20, pattern=r'^[a-zA-Z0-9\+\#]+$')
    
    @field_validator('files')
    @classmethod
    def validate_files_dict(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Files must be a dict")
        if len(v) == 0:
            raise ValueError("At least one file required")
        if len(v) > settings.JUDGE_MAX_FILES:
            raise ValueError(f"Too many files, max {settings.JUDGE_MAX_FILES}")
        
        total_size = 0
        for fname, content in v.items():
            if not isinstance(fname, str) or not isinstance(content, str):
                raise ValueError("Invalid file entry")
            if len(fname) > 100:
                raise ValueError(f"Filename too long: {fname[:30]}")
            if ".." in fname or fname.startswith("/") or "\\" in fname:
                raise ValueError(f"Invalid filename: {fname}")
            if "\x00" in fname or "\x00" in content:
                raise ValueError("Null bytes not allowed")
            
            size = len(content.encode('utf-8'))
            if size > settings.JUDGE_MAX_FILE_SIZE:
                raise ValueError(f"File {fname} too large: {size} bytes")
            total_size += size
        
        if total_size > settings.JUDGE_MAX_TOTAL_SIZE:
            raise ValueError(f"Total size too large: {total_size} bytes")
        
        return v
    
    @field_validator('language')
    @classmethod
    def validate_lang(cls, v):
        allowed = ["c", "cpp", "c++", "python", "py", "javascript", "js"]
        if v.lower() not in allowed:
            raise ValueError(f"Language {v} not supported")
        return v.lower()

@router.get("/")
def list_projects(
    status: Optional[str] = Query(None, max_length=20),
    lang: Optional[str] = Query(None, max_length=20),
    q: Optional[str] = Query(None, max_length=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Sanitize query inputs
        if q:
            q = sanitize_input(q, max_length=100)
            # Prevent regex injection
            q = re.escape(q) if len(q) > 2 else q
        
        if status:
            status = sanitize_input(status, max_length=20)
            allowed_status = ["all", "locked", "available", "progress", "done", "failed", "passed"]
            if status not in allowed_status:
                status = None
        
        if lang:
            lang = sanitize_input(lang, max_length=20)
        
        try:
            projects = db.query(Project).all()
            progresses = db.query(UserProjectProgress).filter(
                UserProjectProgress.user_id == current_user.id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"DB error listing projects for {current_user.username}: {e}")
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        progress_map = {p.project_id: p for p in progresses}
        
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
                "status": prog.status if prog else ("locked" if proj.requires else "available"),
                "progress": prog.progress if prog else None,
                "score": prog.best_score if prog else None,
                "xp": proj.xp,
                "duration": proj.duration,
                "difficulty": proj.difficulty,
                "requires": proj.requires
            }
            # Filters - safe because we control values
            if status and status != "all" and item["status"] != status:
                continue
            if lang and lang != "all" and item["lang"] != lang:
                continue
            if q:
                # Case-insensitive search in Python, not SQL, to avoid injection
                tags_str = ' '.join(item['tags']) if item['tags'] else ''
                search_text = f"{item['name']} {item['desc']} {tags_str}".lower()
                if q.lower() not in search_text:
                    continue
            result.append(item)
        
        result.sort(key=lambda x: x["level_value"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing projects: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list projects")

@router.get("/{slug}")
def get_project(slug: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate slug format to prevent injection
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        raise HTTPException(status_code=400, detail="Invalid project slug format")
    
    if len(slug) > 100:
        raise HTTPException(status_code=400, detail="Slug too long")
    
    try:
        project = db.query(Project).filter(Project.slug == slug).first()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching project {slug}: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    try:
        progress = db.query(UserProjectProgress).filter(
            UserProjectProgress.user_id == current_user.id,
            UserProjectProgress.project_id == project.id
        ).first()
        
        submissions = db.query(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.project_id == project.id
        ).order_by(Submission.created_at.desc()).limit(5).all()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching progress for {slug}: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    
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
        "status": progress.status if progress else ("locked" if project.requires else "available"),
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

@router.post("/{slug}/submit", dependencies=[Depends(judge_rate_limit)])
def submit_project(
    slug: str,
    payload: SubmitRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate slug
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        raise HTTPException(status_code=400, detail="Invalid project slug")
    
    try:
        project = db.query(Project).filter(Project.slug == slug).first()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching project {slug} for submission: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    try:
        progress = db.query(UserProjectProgress).filter(
            UserProjectProgress.user_id == current_user.id,
            UserProjectProgress.project_id == project.id
        ).first()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching progress: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    if progress and progress.status == "locked":
        raise HTTPException(status_code=403, detail="Projet verrouillé, complète les prérequis")
    
    if project.requires:
        prerequisite = db.query(UserProjectProgress).join(Project, Project.id == UserProjectProgress.project_id).filter(
            UserProjectProgress.user_id == current_user.id, Project.slug == project.requires,
            UserProjectProgress.status == "passed").first()
        if not prerequisite:
            raise HTTPException(status_code=403, detail="Project prerequisite has not been completed")

    # Validate files again with security service
    valid, msg = validate_files(payload.files, payload.language)
    if not valid:
        raise HTTPException(status_code=400, detail=f"File validation failed: {msg}")
    
    # Run moulinette with error handling
    try:
        result = run_moulinette(slug, payload.files, payload.language)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Moulinette failed for {slug} by {current_user.username}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Moulinette execution failed")
    
    # Serialize awards per user in PostgreSQL, then reread progress after execution.
    # A failed second submission must not erase an earlier completion.
    xp_earned = 0
    try:
        current_user = db.query(User).filter(User.id == current_user.id).with_for_update().populate_existing().one()
        progress = db.query(UserProjectProgress).filter_by(user_id=current_user.id, project_id=project.id).populate_existing().first()
        already_passed = bool(progress and progress.status == "passed")
        submission = Submission(
            user_id=current_user.id,
            project_id=project.id,
            files=payload.files,
            language=payload.language,
            status="success" if result["score"] >= 80 else "failed",
            score=result["score"],
            tests=result["tests"],
            logs=result["logs"][:10000]  # Truncate logs to prevent DB bloat
        )
        db.add(submission)
        
        # Check plagiarism (non-critical)
        try:
            other_subs = db.query(Submission).filter(
                Submission.project_id == project.id,
                Submission.user_id != current_user.id
            ).order_by(Submission.created_at.desc()).limit(20).all()
            
            existing_codes = ["".join(s.files.values()) for s in other_subs if s.files]
            
            if existing_codes:
                new_code = "".join(payload.files.values())
                plag = IntegrityService.check_plagiarism(new_code, existing_codes)
                submission.similarity_score = plag["similarity"]
                if plag["is_plagiarism"]:
                    submission.integrity_flags = ["high_similarity"]
                    logger.warning(f"High similarity detected for {current_user.username} on {slug}: {plag['similarity']}%")
        except Exception as e:
            logger.warning(f"Plagiarism check failed: {e}")
        
        # Update progress
        if not progress:
            progress = UserProjectProgress(
                user_id=current_user.id,
                project_id=project.id,
                status="progress",
                progress=0
            )
            db.add(progress)
        
        progress.attempts = (progress.attempts or 0) + 1
        progress.progress = max(progress.progress or 0, min(100, result["score"]))
        if result["score"] > (progress.best_score or 0):
            progress.best_score = result["score"]
        
        unlocked = []
        if result["score"] >= 80:
            progress.status = "passed"
            try:
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
                    unlocked.append(np.slug)
                
                if not already_passed:
                    from datetime import datetime
                    progress.completed_at = datetime.utcnow()
                    award = GamificationService.complete_project(current_user, project.xp, result["score"], db, commit=False)
                    xp_earned = award["xp_earned"]
                    SkillGraphService.update_from_submission(current_user, submission, project, result["score"], db, commit=False)
            except Exception as e:
                logger.error(f"Error updating progress after pass: {e}", exc_info=True)
                raise
        elif not already_passed:
            progress.status = "progress"
        
        db.commit()
        db.refresh(submission)
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error saving submission for {slug}: {e}")
        raise HTTPException(status_code=503, detail="Failed to save submission")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error saving submission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error")
    
    # Log audit (non-critical)
    try:
        IntegrityService.log_action(
            current_user.id, "project_submit", "project", project.id,
            {"score": result["score"], "slug": slug, "ip": request.client.host if request.client else "unknown"}, db=db
        )
    except Exception as e:
        logger.warning(f"Failed to log audit: {e}")
    
    return {
        "ok": True,
        "submission_id": submission.id,
        "score": result["score"],
        "tests": result["tests"],
        "logs": result["logs"],
        "status": progress.status,
        "progress": progress.progress,
        "xp_earned": xp_earned,
        "next_projects_unlocked": unlocked
    }

@router.get("/{slug}/submissions")
def get_submissions(slug: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        raise HTTPException(status_code=400, detail="Invalid slug")
    
    try:
        project = db.query(Project).filter(Project.slug == slug).first()
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")
        
        subs = db.query(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.project_id == project.id
        ).order_by(Submission.created_at.desc()).all()
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching submissions: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    return [
        {
            "id": s.id,
            "status": s.status,
            "score": s.score,
            "tests": s.tests,
            "logs": s.logs[:5000] if s.logs else None,  # Truncate for response
            "similarity": s.similarity_score,
            "created_at": s.created_at.isoformat() if s.created_at else None
        } for s in subs
    ]

@router.post("/seed", dependencies=[Depends(require_admin)])
def seed_projects(db: Session = Depends(get_db)):
    """Seed default projects - restricted to development"""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Seeding not allowed in production")
    
    default_projects = [
        {"slug": "get_next_line", "name": "get_next_line", "description": "Lis une ligne depuis un file descriptor, sans jamais perdre le fil.", "level": "Niveau 1", "level_value": 1.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "I/O", "Buffer"], "xp": 1200, "duration": "1 sem.", "difficulty": 2, "status_default": "done", "objectives": ["Gérer plusieurs FD", "Gérer BUFFER_SIZE variable"]},
        {"slug": "ft_printf", "name": "ft_printf", "description": "Recode la fonction variadique la plus utilisée de la libc.", "level": "Niveau 2", "level_value": 2.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "Variadic", "Parsing"], "xp": 1500, "duration": "2 sem.", "difficulty": 3, "status_default": "done"},
        {"slug": "minishell", "name": "minishell", "description": "Écris ton propre shell : parsing, pipes, redirections, builtins et signaux.", "level": "Niveau 4", "level_value": 4.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Duo", "Unix", "Parsing"], "xp": 3200, "duration": "4 sem.", "difficulty": 5, "status_default": "progress"},
        {"slug": "philosophers", "name": "philosophers", "description": "Résous le problème des philosophes avec threads et mutex, sans data race.", "level": "Niveau 3", "level_value": 3.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "Threads", "Concurrence"], "xp": 2100, "duration": "2 sem.", "difficulty": 4, "status_default": "available"},
        {"slug": "netpractice", "name": "netpractice", "description": "Configure des réseaux TCP/IP et comprends enfin le masque de sous-réseau.", "level": "Niveau 4", "level_value": 4.2, "lang": "Réseau", "lang_color": "#2ECC71", "tags": ["Solo", "Réseau"], "xp": 1100, "duration": "3 j.", "difficulty": 2, "status_default": "done"},
        {"slug": "cub3d", "name": "cub3d", "description": "Un moteur de rendu 3D en raycasting, inspiré du légendaire Wolfenstein 3D.", "level": "Niveau 5", "level_value": 5.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Duo", "Graphique", "Maths"], "xp": 3600, "duration": "4 sem.", "difficulty": 5, "status_default": "available"},
        {"slug": "webserv", "name": "webserv", "description": "Implémente un serveur HTTP/1.1 conforme, non-bloquant, façon NGINX.", "level": "Niveau 6", "level_value": 6.0, "lang": "C++", "lang_color": "#F26FA4", "tags": ["Trio", "Réseau", "HTTP"], "xp": 4200, "duration": "5 sem.", "difficulty": 5, "status_default": "locked", "requires": "minishell"},
        {"slug": "inception", "name": "inception", "description": "Orchestre une infrastructure multi-conteneurs avec Docker Compose.", "level": "Niveau 6", "level_value": 6.5, "lang": "Docker", "lang_color": "#3B9EFF", "tags": ["Solo", "DevOps", "Docker"], "xp": 2800, "duration": "3 sem.", "difficulty": 4, "status_default": "locked", "requires": "webserv"},
        {"slug": "ft_transcendence", "name": "ft_transcendence", "description": "Le projet final : une SPA temps réel avec un Pong multijoueur en ligne.", "level": "Niveau 8", "level_value": 8.0, "lang": "Web", "lang_color": "#F5B942", "tags": ["Groupe", "Fullstack", "WebSocket"], "xp": 8000, "duration": "8 sem.", "difficulty": 5, "status_default": "locked", "requires": "inception"},
    ]
    
    try:
        for data in default_projects:
            existing = db.query(Project).filter(Project.slug == data["slug"]).first()
            if not existing:
                p = Project(**data)
                db.add(p)
        db.commit()
        return {"ok": True, "count": len(default_projects)}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Seed failed: {e}")
        raise HTTPException(status_code=500, detail="Seed failed")
