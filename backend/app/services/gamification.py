"""
Gamification Layer 2.0 — XP, Level, Badges, Streak, Daily Missions
Level system: 0.00 to 21.00 continuous
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models import DailyMission, Badge, UserBadge, ArenaMatch
from datetime import datetime, timedelta
import random
import math

# XP thresholds for levels (exponential)
LEVEL_THRESHOLDS = [0]
for i in range(1, 22):
    # Each level requires more XP
    LEVEL_THRESHOLDS.append(LEVEL_THRESHOLDS[-1] + int(1000 * (1.25 ** i)))

def xp_to_level(xp: int) -> float:
    """Convert XP to level 0.00 - 21.00"""
    level = 0
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i
        else:
            break
    # Fractional part
    if level < 21:
        next_threshold = LEVEL_THRESHOLDS[level + 1] if level + 1 < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
        current_threshold = LEVEL_THRESHOLDS[level]
        if next_threshold > current_threshold:
            progress = (xp - current_threshold) / (next_threshold - current_threshold)
            level = level + progress
    return round(min(21.0, level), 2)

def level_to_xp(level: float) -> int:
    """Convert level to minimum XP"""
    int_level = int(level)
    if int_level >= len(LEVEL_THRESHOLDS):
        return LEVEL_THRESHOLDS[-1]
    base = LEVEL_THRESHOLDS[int_level]
    frac = level - int_level
    if frac > 0 and int_level + 1 < len(LEVEL_THRESHOLDS):
        next_thr = LEVEL_THRESHOLDS[int_level + 1]
        base += int((next_thr - base) * frac)
    return base

def calculate_level_progress(xp: int) -> int:
    """0-100 progress to next level"""
    level = xp_to_level(xp)
    int_level = int(level)
    frac = level - int_level
    return int(frac * 100)

class GamificationService:
    @staticmethod
    def add_xp(user: User, amount: int, reason: str, db: Session, commit: bool = True) -> User:
        if type(amount) is not int or amount < 0:
            raise ValueError('XP awards must be nonnegative trusted integers')
        old_level = xp_to_level(user.xp)
        user.xp += amount
        new_level = xp_to_level(user.xp)
        
        user.level = new_level
        # Update xp_to_next
        next_level = min(21, int(new_level) + 1)
        if next_level < len(LEVEL_THRESHOLDS):
            user.xp_to_next = LEVEL_THRESHOLDS[next_level] - user.xp
        else:
            user.xp_to_next = 0
        
        # Level up bonus
        if int(new_level) > int(old_level):
            user.jetons += 1
            user.account_value += 500
        
        # Update streak logic would be here
        user.last_activity = datetime.utcnow()
        
        if commit:
            db.commit()
        return user
    
    @staticmethod
    def complete_project(user: User, project_xp: int, score: int, db: Session, commit: bool = True) -> dict:
        if type(project_xp) is not int or project_xp < 0 or type(score) is not int or not 0 <= score <= 100:
            raise ValueError('Invalid trusted project award')
        # XP based on score
        multiplier = score / 100
        xp_earned = int(project_xp * multiplier)
        
        # Bonus for 100%
        if score >= 100:
            xp_earned = int(xp_earned * 1.15)
        
        old_level = user.level
        GamificationService.add_xp(user, xp_earned, f"Project completed: {score}%", db, commit=False)
        user.projects_done += 1
        
        # Accuracy update
        # Simplified moving average
        user.accuracy = int((user.accuracy * 0.9 + score * 0.1)) if user.accuracy else score
        
        if commit:
            db.commit()
        
        return {
            "xp_earned": xp_earned,
            "old_level": old_level,
            "new_level": user.level,
            "leveled_up": int(user.level) > int(old_level),
            "total_xp": user.xp
        }
    
    @staticmethod
    def generate_daily_mission(user: User, db: Session):
        # Check if already has mission today
        today = datetime.utcnow().date()
        existing = db.query(DailyMission).filter(
            DailyMission.user_id == user.id,
            DailyMission.created_at >= datetime.combine(today, datetime.min.time())
        ).first()
        if existing:
            return existing
        
        missions_pool = [
            {"title": "Reverse a linked list", "skill": "Structures de données", "difficulty": 3, "xp": 120},
            {"title": "Implement binary search", "skill": "Algorithms", "difficulty": 2, "xp": 100},
            {"title": "Fix memory leak in sample", "skill": "Memory", "difficulty": 4, "xp": 150},
            {"title": "Parse HTTP request", "skill": "Réseau", "difficulty": 3, "xp": 130},
            {"title": "Thread-safe counter", "skill": "Threads", "difficulty": 4, "xp": 160},
            {"title": "Écrire un Makefile propre", "skill": "Tooling", "difficulty": 1, "xp": 80},
        ]
        
        # Pick based on user's weakest skill
        weakest = "Algorithms"
        if user.skills:
            # Find lowest skill
            min_val = 100
            for group, skills in user.skills.items():
                if isinstance(skills, dict):
                    for s, v in skills.items():
                        if v < min_val:
                            min_val = v
                            weakest = s
        
        # Filter relevant
        relevant = [m for m in missions_pool if weakest.lower() in m["skill"].lower() or m["skill"] == "Algorithms"]
        chosen = random.choice(relevant or missions_pool)
        
        mission = DailyMission(
            user_id=user.id,
            title=chosen["title"],
            description=f"Mission quotidienne pour améliorer {chosen['skill']}",
            difficulty=chosen["difficulty"],
            reward_xp=0,  # Suggestions are not executable missions and award no XP.
            skill=chosen["skill"],
            status="available",
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        db.add(mission)
        db.commit()
        db.refresh(mission)
        return mission
    
    @staticmethod
    def check_streak(user: User, db: Session) -> dict:
        # Read-only measured submission streak in UTC. Repeated page views may
        # neither create activity nor increment a counter. No reward is issued.
        from app.models.submission import Submission
        dates={row[0].date() for row in db.query(Submission.created_at).filter(
            Submission.user_id==user.id,Submission.created_at>=datetime.utcnow()-timedelta(days=366)).all()}
        today=datetime.utcnow().date()
        cursor=today if today in dates else today-timedelta(days=1)
        streak=0
        while cursor in dates:
            streak+=1; cursor-=timedelta(days=1)
        return {'streak':streak,'burnout_risk':False,'recommendation':None,
                'basis':'distinct submission days UTC; no medical inference'}

    @staticmethod
    def award_badge(user: User, badge_name: str, db: Session):
        badge = db.query(Badge).filter(Badge.name == badge_name).first()
        if not badge:
            return None
        
        existing = db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == badge.id
        ).first()
        if existing:
            return existing
        
        ub = UserBadge(user_id=user.id, badge_id=badge.id)
        db.add(ub)
        db.commit()
        return ub
