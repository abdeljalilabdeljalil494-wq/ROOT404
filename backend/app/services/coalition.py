"""
Coalition System — Houses, scoring, wars
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.coalition import Coalition, CoalitionMember, CoalitionWar
from app.models.user import User
from app.models.project import UserProjectProgress
from datetime import datetime, timedelta

class CoalitionService:
    @staticmethod
    def get_leaderboard(db: Session):
        coalitions = db.query(Coalition).order_by(Coalition.points.desc()).all()
        result = []
        for idx, c in enumerate(coalitions, 1):
            result.append({
                "id": c.id,
                "rank": idx,
                "name": c.name,
                "color": c.color,
                "points": c.points,
                "members": c.members_count,
                "wins": c.wins,
                "trend": c.trend,
                "motto": c.motto
            })
        return result
    
    @staticmethod
    def assign_user_to_coalition(user: User, db: Session, coalition_id: str = None):
        """
        Assign user to coalition - auto balance or chosen
        """
        if coalition_id:
            coalition = db.query(Coalition).filter(Coalition.id == coalition_id).first()
        else:
            # Auto-assign to smallest coalition for balance
            coalition = db.query(Coalition).order_by(Coalition.members_count.asc()).first()
        
        if not coalition:
            return None
        
        # Check if already member
        existing = db.query(CoalitionMember).filter(
            CoalitionMember.user_id == user.id
        ).first()
        if existing:
            return existing
        
        member = CoalitionMember(
            coalition_id=coalition.id,
            user_id=user.id
        )
        coalition.members_count += 1
        user.coalition_id = coalition.id
        
        db.add(member)
        db.commit()
        return member
    
    @staticmethod
    def add_points(coalition_id: str, points: int, reason: str, db: Session):
        coalition = db.query(Coalition).filter(Coalition.id == coalition_id).first()
        if coalition:
            coalition.points += points
            db.commit()
        return coalition
    
    @staticmethod
    def calculate_user_contribution(user_id: str, db: Session) -> int:
        """
        Calculate how many points user contributed to coalition
        """
        # Projects done * xp + correction points
        progress = db.query(UserProjectProgress).filter(
            UserProjectProgress.user_id == user_id,
            UserProjectProgress.status == "passed"
        ).all()
        # Simplified: 100 points per project + correction bonus
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0
        return len(progress) * 100 + (user.correction_points // 10)
    
    @staticmethod
    def create_war(name: str, description: str, duration_hours: int, db: Session):
        now = datetime.utcnow()
        war = CoalitionWar(
            name=name,
            description=description,
            start_at=now,
            end_at=now + timedelta(hours=duration_hours),
            status="active",
            points={}
        )
        db.add(war)
        db.commit()
        db.refresh(war)
        return war
    
    @staticmethod
    def get_active_wars(db: Session):
        return db.query(CoalitionWar).filter(
            CoalitionWar.status == "active",
            CoalitionWar.end_at >= datetime.utcnow()
        ).all()
    
    @staticmethod
    def seed_default_coalitions(db: Session):
        """Seed the 4 default coalitions if not exist"""
        defaults = [
            {"name": "The Phoenix", "color": "#F8851F", "motto": "Renaître de chaque segfault.", "points": 7286, "members_count": 312, "wins": 14, "trend": "+320"},
            {"name": "Neon Wolves", "color": "#3B9EFF", "motto": "La meute compile ensemble.", "points": 6941, "members_count": 298, "wins": 11, "trend": "+180"},
            {"name": "Data Vipers", "color": "#2ECC71", "motto": "Silencieux, précis, mortels.", "points": 6402, "members_count": 305, "wins": 9, "trend": "+95"},
            {"name": "Sand Foxes", "color": "#F5B942", "motto": "Rusés dans le désert du code.", "points": 5877, "members_count": 281, "wins": 8, "trend": "+60"},
        ]
        for data in defaults:
            existing = db.query(Coalition).filter(Coalition.name == data["name"]).first()
            if not existing:
                c = Coalition(**data)
                db.add(c)
        db.commit()
