"""
Integrity / Trust Score — Anti-Cheating multi-factor
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.submission import Submission
from app.models import AuditLog
from typing import List, Dict
import hashlib
import time
import random

class IntegrityService:
    @staticmethod
    def calculate_score(user: User, db: Session) -> dict:
        """
        Calculate integrity score 0-100
        Factors:
        - Code Similarity
        - Typing Pattern
        - Submission Pattern
        - AI Dependency
        - Peer Review validity
        """
        base = 100
        
        # Similarity check - look at recent submissions
        recent_subs = db.query(Submission).filter(
            Submission.user_id == user.id
        ).order_by(Submission.created_at.desc()).limit(10).all()
        
        similarity = 2  # Default low
        if recent_subs:
            # Simulate similarity check
            avg_similarity = sum(s.similarity_score or 0 for s in recent_subs) / len(recent_subs)
            similarity = int(avg_similarity)
        
        # Typing pattern - would be real in production with keystroke dynamics
        typing = "Normal"
        if user.integrity_score and user.integrity_score < 80:
            typing = "Suspicious"
        
        # Submission pattern - rapid submissions
        submission_pattern = "Normal"
        if len(recent_subs) >= 3:
            # Check if 3 submissions in last hour
            from datetime import datetime, timedelta
            recent_hour = [s for s in recent_subs if s.created_at and s.created_at >= datetime.utcnow() - timedelta(hours=1)]
            if len(recent_hour) >= 3:
                submission_pattern = "Rapid"
                base -= 10
        
        # AI Dependency
        ai_dependency = "Low"
        # Would track AI mentor usage
        # For now mock based on user level vs projects
        if user.projects_done > 0 and user.xp < 1000:
            ai_dependency = "High"
            base -= 15
        
        # Peer review
        peer_review = "Valid"
        
        final_score = max(0, min(100, base - similarity))
        
        return {
            "total": final_score,
            "rows": [
                {"label": "Code Similarity", "value": f"{similarity}%", "tone": "ok" if similarity < 10 else "warn" if similarity < 30 else "danger"},
                {"label": "Typing Pattern", "value": typing, "tone": "ok" if typing == "Normal" else "warn"},
                {"label": "Submission Pattern", "value": submission_pattern, "tone": "ok" if submission_pattern == "Normal" else "warn"},
                {"label": "AI Dependency", "value": ai_dependency, "tone": "ok" if ai_dependency == "Low" else "warn" if ai_dependency == "Medium" else "danger"},
                {"label": "Peer Review", "value": peer_review, "tone": "ok"},
            ],
            "is_flagged": final_score < 70,
            "requires_review": final_score < 50
        }
    
    @staticmethod
    def check_plagiarism(new_code: str, existing_codes: List[str]) -> Dict:
        """
        AST-based plagiarism detection (simplified)
        """
        def normalize_code(code: str) -> str:
            # Remove whitespace, comments, etc. for fingerprinting
            lines = code.split('\n')
            cleaned = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('#'):
                    continue
                # Remove inline comments
                if '//' in line:
                    line = line.split('//')[0]
                cleaned.append(line)
            return ' '.join(cleaned)
        
        def fingerprint(code: str) -> str:
            norm = normalize_code(code)
            return hashlib.md5(norm.encode()).hexdigest()
        
        new_fp = fingerprint(new_code)
        max_similarity = 0
        most_similar = None
        
        for idx, existing in enumerate(existing_codes):
            exist_fp = fingerprint(existing)
            if new_fp == exist_fp:
                max_similarity = 100
                most_similar = idx
                break
            
            # Simple similarity on normalized code
            # In production would use AST comparison
            norm_new = normalize_code(new_code)
            norm_exist = normalize_code(existing)
            
            # Jaccard similarity on tokens
            tokens_new = set(norm_new.split())
            tokens_exist = set(norm_exist.split())
            if tokens_new and tokens_exist:
                intersection = len(tokens_new & tokens_exist)
                union = len(tokens_new | tokens_exist)
                sim = (intersection / union * 100) if union else 0
                if sim > max_similarity:
                    max_similarity = sim
                    most_similar = idx
        
        return {
            "similarity": round(max_similarity, 2),
            "is_plagiarism": max_similarity > 80,
            "requires_human_review": max_similarity > 60,
            "most_similar_index": most_similar
        }
    
    @staticmethod
    def log_action(user_id: str, action: str, resource_type: str = None, resource_id: str = None, details: dict = None, ip: str = None, db: Session = None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip
        )
        if db:
            db.add(log)
            db.commit()
        return log
    
    @staticmethod
    def analyze_typing_pattern(keystrokes: List[dict]) -> dict:
        """
        Analyze typing pattern for anomalies
        keystrokes: [{key, timestamp, duration}]
        """
        if not keystrokes or len(keystrokes) < 10:
            return {"pattern": "Normal", "confidence": 0.5}
        
        # Calculate average time between keystrokes
        intervals = []
        for i in range(1, len(keystrokes)):
            intervals.append(keystrokes[i]["timestamp"] - keystrokes[i-1]["timestamp"])
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals) if intervals else 0
        
        # Very low variance + very fast typing = potential paste
        if variance < 10 and avg_interval < 50:
            return {"pattern": "Suspicious - possible paste", "confidence": 0.8, "avg_interval": avg_interval, "variance": variance}
        
        # Human typing has higher variance
        return {"pattern": "Normal", "confidence": 0.9, "avg_interval": avg_interval, "variance": variance}
