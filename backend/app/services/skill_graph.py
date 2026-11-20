"""
Skill Graph — dynamic skill measurement
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import UserProjectProgress, Project
from app.models.submission import Submission
from typing import Dict, List

SKILL_GROUPS = {
    "C": ["Variables", "Pointers", "Memory", "Structs", "Functions"],
    "Algorithms": ["Sorting", "Recursion", "Complexity", "Graphs"],
    "Systems": ["Processes", "Threads", "Signals", "Sockets"],
    "Tooling": ["Git", "Docker", "Makefile", "Valgrind"]
}

PROJECT_SKILL_MAP = {
    "get_next_line": {"C": {"Variables": 10, "Pointers": 20, "Memory": 15}},
    "ft_printf": {"C": {"Variables": 15, "Functions": 20, "Memory": 10}},
    "minishell": {"C": {"Pointers": 25, "Memory": 20, "Structs": 15}, "Systems": {"Processes": 20, "Signals": 15}},
    "philosophers": {"C": {"Memory": 15, "Structs": 10}, "Systems": {"Threads": 30, "Signals": 10}},
    "netpractice": {"Systems": {"Sockets": 25, "Processes": 10}},
    "cub3d": {"C": {"Memory": 20, "Structs": 20}, "Algorithms": {"Graphs": 15}},
    "webserv": {"Systems": {"Sockets": 30, "Processes": 20}, "Tooling": {"Docker": 10}},
}

class SkillGraphService:
    @staticmethod
    def initialize_skills() -> Dict:
        graph = {}
        for group, skills in SKILL_GROUPS.items():
            graph[group] = {skill: 0 for skill in skills}
        return graph
    
    @staticmethod
    def update_from_submission(user: User, submission: Submission, project: Project, score: int, db: Session, commit: bool = True) -> Dict:
        if not user.skills:
            user.skills = SkillGraphService.initialize_skills()
        
        # Get skill mapping for project
        mapping = PROJECT_SKILL_MAP.get(project.slug, {})
        
        # Update skills based on score
        for group, skills in mapping.items():
            if group not in user.skills:
                user.skills[group] = {}
            for skill, weight in skills.items():
                current = user.skills[group].get(skill, 0)
                # Increase based on score and weight
                gain = (weight * score / 100) * 0.1  # 10% of weight scaled by score
                new_val = min(100, current + gain)
                user.skills[group][skill] = int(new_val)
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "skills")
        if commit:
            db.commit()
        return user.skills
    
    @staticmethod
    def get_knowledge_gaps(user: User) -> List[dict]:
        if not user.skills:
            return []
        
        gaps = []
        for group, skills in user.skills.items():
            if isinstance(skills, dict):
                for skill, value in skills.items():
                    if value < 50:
                        gaps.append({
                            "group": group,
                            "name": skill,
                            "value": value,
                            "priority": "high" if value < 30 else "medium"
                        })
        
        # Sort by lowest first
        gaps.sort(key=lambda x: x["value"])
        return gaps[:5]
    
    @staticmethod
    def recommend_micro_challenges(gaps: List[dict]) -> List[dict]:
        challenges = []
        for gap in gaps:
            challenges.append({
                "skill": gap["name"],
                "group": gap["group"],
                "title": f"Micro-challenge: {gap['name']}",
                "description": f"Renforce ta compétence en {gap['name']} ({gap['group']})",
                "difficulty": 1 if gap["value"] < 30 else 2,
                "estimated_time": "15-20 min",
                "xp": 50 if gap["value"] < 30 else 80
            })
        return challenges
    
    @staticmethod
    def get_skill_graph_for_user(user: User) -> List[dict]:
        if not user.skills:
            user.skills = SkillGraphService.initialize_skills()
        
        # Convert to frontend format
        result = []
        colors = {"C": "#3B9EFF", "Algorithms": "#F8851F", "Systems": "#2ECC71", "Tooling": "#B37BFF"}
        for group, skills in user.skills.items():
            if isinstance(skills, dict):
                result.append({
                    "group": group,
                    "color": colors.get(group, "#F8851F"),
                    "skills": [{"name": k, "value": v} for k, v in skills.items()]
                })
        return result
