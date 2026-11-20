"""
Black Hole & Survival Timer System
Inspired by 42's Black Hole: account freeze if insufficient progress
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import UserProjectProgress
import math

class BlackHoleService:
    @staticmethod
    def calculate_days_left(user: User, db: Session) -> int:
        """
        Calculate remaining days before Black Hole absorption
        Based on: last activity, level progress, projects completed
        """
        if not user.last_activity:
            return user.blackhole_days_left
        
        days_since_active = (datetime.utcnow() - user.last_activity).days
        
        # Base decay: lose 1 day per inactive day
        # But gain days by completing projects
        recent_progress = db.query(UserProjectProgress).filter(
            UserProjectProgress.user_id == user.id,
            UserProjectProgress.completed_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Each project completed in last 30 days gives +7 days
        bonus = recent_progress * 7
        
        # Level factor: higher level = more leniency
        level_bonus = int(user.level * 2)
        
        remaining = user.blackhole_total - days_since_active + bonus + level_bonus
        return max(0, min(user.blackhole_total, remaining))
    
    @staticmethod
    def check_warning_zone(user: User, days_left: int) -> bool:
        """Is user in warning zone?"""
        return days_left <= 7 and days_left > 0
    
    @staticmethod
    def check_absorption(user: User, days_left: int) -> bool:
        """Should user be absorbed?"""
        return days_left <= 0
    
    @staticmethod
    def update_user_blackhole(user: User, db: Session):
        # Serialize with activity/XP updates and discard stale identity-map state.
        user = db.query(User).filter(User.id == user.id).with_for_update().populate_existing().one()
        days_left = BlackHoleService.calculate_days_left(user, db)
        user.blackhole_days_left = days_left
        user.blackhole_warning = BlackHoleService.check_warning_zone(user, days_left)
        
        if BlackHoleService.check_absorption(user, days_left):
            user.is_active = False  # Freeze account
            # In real 42, account is frozen and priority redistributed
            # Here we keep it frozen until admin intervention or activity
        
        db.commit()
        return user
    
    @staticmethod
    def get_recommendation(user: User, days_left: int) -> dict:
        if days_left > 30:
            return {
                "status": "safe",
                "message": f"Tu as {days_left} jours devant toi. Continue à ce rythme !",
                "suggested_action": "Projet recommandé : continue ton cursus actuel"
            }
        elif days_left > 7:
            return {
                "status": "watch",
                "message": f"Attention : {days_left} jours restants. Ton activité a baissé.",
                "suggested_action": "Termine un projet cette semaine pour gagner +7 jours"
            }
        elif days_left > 0:
            return {
                "status": "warning",
                "message": f"⚠️ Zone de danger : {days_left} jours avant Black Hole !",
                "suggested_action": "Action immédiate : complète une Daily Mission ou réserve une correction"
            }
        else:
            return {
                "status": "absorbed",
                "message": "🕳️ Black Hole : ton compte est gelé temporairement",
                "suggested_action": "Contacte un admin ou complète la Piscine de rattrapage"
            }
    
    @staticmethod
    def run_daily_check(db: Session):
        """Cron job to check all users"""
        users = db.query(User).filter(User.is_active == True).all()
        absorbed = []
        warned = []
        
        for user in users:
            old_left = user.blackhole_days_left
            BlackHoleService.update_user_blackhole(user, db)
            
            if user.blackhole_days_left <= 0 and old_left > 0:
                absorbed.append(user.username)
            elif user.blackhole_warning and old_left > 7:
                warned.append(user.username)
        
        return {"absorbed": absorbed, "warned": warned, "checked": len(users)}
