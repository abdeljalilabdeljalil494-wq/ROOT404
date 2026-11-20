"""
Smart Peer Matchmaking & Correction Engine
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.user import User
from app.models.correction import Correction, CorrectionSlot
from app.models.project import Project, UserProjectProgress
from app.models.submission import Submission
from datetime import datetime, timedelta
import random

class CorrectionService:
    @staticmethod
    def find_best_corrector(project_id: str, author_id: str, db: Session, language_pref: str = None) -> User:
        """
        Smart Peer Matchmaking algorithm:
        - Level >= required level
        - Same project done or higher
        - Availability
        - Language preference
        - Reputation Score
        - Avoid recent same pairs
        - Load balancing
        """
        author = db.query(User).filter(User.id == author_id).first()
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return None
        
        # Find users who completed this project
        completed_user_ids = db.query(UserProjectProgress.user_id).filter(
            UserProjectProgress.project_id == project_id,
            UserProjectProgress.status == "passed"
        ).all()
        completed_user_ids = [u[0] for u in completed_user_ids if u[0] != author_id]
        
        if not completed_user_ids:
            # Fallback: any user with higher level
            candidates = db.query(User).filter(
                User.id != author_id,
                User.level >= (project.level_value or 1),
                User.is_active == True
            ).all()
        else:
            candidates = db.query(User).filter(User.id.in_(completed_user_ids)).all()
        
        if not candidates:
            return None
        
        # Score candidates
        scored = []
        for cand in candidates:
            score = 0
            
            # Reputation bonus
            score += cand.reputation * 0.5
            
            # Level proximity: prefer close but higher
            level_diff = cand.level - (author.level if author else 0)
            if 0 <= level_diff <= 3:
                score += 20
            elif level_diff > 3:
                score += 10
            
            # Campus bonus if same
            if author and cand.campus == author.campus:
                score += 15
            
            # Avoid recent corrections together (last 7 days)
            recent = db.query(Correction).filter(
                or_(
                    and_(Correction.author_id == author_id, Correction.corrector_id == cand.id),
                    and_(Correction.author_id == cand.id, Correction.corrector_id == author_id)
                ),
                Correction.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            score -= recent * 30  # Penalize recent pairs
            
            # Availability: has open slots?
            open_slots = db.query(CorrectionSlot).filter(
                CorrectionSlot.corrector_id == cand.id,
                CorrectionSlot.is_booked == False,
                CorrectionSlot.start_time >= datetime.utcnow()
            ).count()
            score += open_slots * 10
            
            # Language preference (simplified)
            if language_pref and cand.id:  # In real app, user has language pref
                score += 5
            
            # Random factor to avoid deterministic
            score += random.uniform(-5, 5)
            
            scored.append((cand, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else None
    
    @staticmethod
    def create_correction_request(submission_id: str, author_id: str, db: Session) -> Correction:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return None
        
        corrector = CorrectionService.find_best_corrector(
            submission.project_id, author_id, db
        )
        
        correction = Correction(
            submission_id=submission_id,
            author_id=author_id,
            corrector_id=corrector.id if corrector else None,
            status="pending" if corrector else "searching",
            checklist=CorrectionService.get_checklist_for_project(submission.project_id, db)
        )
        db.add(correction)
        db.commit()
        db.refresh(correction)
        return correction
    
    @staticmethod
    def get_checklist_for_project(project_id: str, db: Session) -> list:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []
        
        # Generate checklist based on project type
        base = [
            {"item": "Le code compile sans warnings", "checked": False, "required": True},
            {"item": "Norminette OK", "checked": False, "required": True},
            {"item": "Pas de fuites mémoire", "checked": False, "required": True},
            {"item": "Gestion des cas d'erreur", "checked": False, "required": False},
            {"item": "Code lisible et commenté si nécessaire", "checked": False, "required": False},
        ]
        
        if project.lang == "C":
            base.extend([
                {"item": "Makefile avec règles all, clean, fclean, re", "checked": False, "required": True},
                {"item": "Pas de variable globale non autorisée", "checked": False, "required": True},
            ])
        
        if "minishell" in (project.slug or ""):
            base.extend([
                {"item": "Builtins fonctionnels (echo, cd, pwd, env, export, unset, exit)", "checked": False, "required": True},
                {"item": "Pipes et redirections", "checked": False, "required": True},
                {"item": "Signaux gérés comme bash", "checked": False, "required": True},
                {"item": "Heredoc", "checked": False, "required": False},
            ])
        
        return base
    
    @staticmethod
    def calculate_correction_points(correction: Correction) -> int:
        base = 50
        if correction.score and correction.score >= 80:
            base += 20
        # Bonus for thorough checklist
        if correction.checklist:
            checked = sum(1 for item in correction.checklist if item.get("checked"))
            total = len(correction.checklist)
            if total > 0 and checked / total >= 0.8:
                base += 10
        return base
    
    @staticmethod
    def get_pending_corrections(user_id: str, db: Session, role: str = "corrector"):
        if role == "corrector":
            return db.query(Correction).filter(
                Correction.corrector_id == user_id,
                Correction.status.in_(["pending", "scheduled"])
            ).all()
        else:
            return db.query(Correction).filter(
                Correction.author_id == user_id,
                Correction.status.in_(["pending", "searching", "scheduled"])
            ).all()
