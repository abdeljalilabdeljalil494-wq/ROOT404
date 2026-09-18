import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import init_db, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.services.skill_graph import SkillGraphService
from app.services.coalition import CoalitionService

# Ensure DB tables exist before any test
init_db()

# Seed demo data
db = SessionLocal()
try:
    # Seed coalitions
    CoalitionService.seed_default_coalitions(db)
    
    # Seed projects if empty
    if db.query(Project).count() == 0:
        default_projects = [
            {"slug": "get_next_line", "name": "get_next_line", "description": "Lis une ligne depuis un file descriptor, sans jamais perdre le fil.", "level": "Niveau 1", "level_value": 1.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "I/O", "Buffer"], "xp": 1200, "duration": "1 sem.", "difficulty": 2, "status_default": "done"},
            {"slug": "ft_printf", "name": "ft_printf", "description": "Recode la fonction variadique la plus utilisée de la libc.", "level": "Niveau 2", "level_value": 2.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "Variadic", "Parsing"], "xp": 1500, "duration": "2 sem.", "difficulty": 3, "status_default": "done"},
            {"slug": "minishell", "name": "minishell", "description": "Écris ton propre shell : parsing, pipes, redirections, builtins et signaux.", "level": "Niveau 4", "level_value": 4.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Duo", "Unix", "Parsing"], "xp": 3200, "duration": "4 sem.", "difficulty": 5, "status_default": "progress"},
            {"slug": "philosophers", "name": "philosophers", "description": "Résous le problème des philosophes avec threads et mutex, sans data race.", "level": "Niveau 3", "level_value": 3.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "Threads", "Concurrence"], "xp": 2100, "duration": "2 sem.", "difficulty": 4, "status_default": "available"},
            {"slug": "netpractice", "name": "netpractice", "description": "Configure des réseaux TCP/IP et comprends enfin le masque de sous-réseau.", "level": "Niveau 4", "level_value": 4.2, "lang": "Réseau", "lang_color": "#2ECC71", "tags": ["Solo", "Réseau"], "xp": 1100, "duration": "3 j.", "difficulty": 2, "status_default": "done"},
            {"slug": "cub3d", "name": "cub3d", "description": "Un moteur de rendu 3D en raycasting, inspiré du légendaire Wolfenstein 3D.", "level": "Niveau 5", "level_value": 5.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Duo", "Graphique", "Maths"], "xp": 3600, "duration": "4 sem.", "difficulty": 5, "status_default": "available"},
            {"slug": "webserv", "name": "webserv", "description": "Implémente un serveur HTTP/1.1 conforme, non-bloquant, façon NGINX.", "level": "Niveau 6", "level_value": 6.0, "lang": "C++", "lang_color": "#F26FA4", "tags": ["Trio", "Réseau", "HTTP"], "xp": 4200, "duration": "5 sem.", "difficulty": 5, "status_default": "locked", "requires": "minishell"},
            {"slug": "inception", "name": "inception", "description": "Orchestre une infrastructure multi-conteneurs avec Docker Compose.", "level": "Niveau 6", "level_value": 6.5, "lang": "Docker", "lang_color": "#3B9EFF", "tags": ["Solo", "DevOps", "Docker"], "xp": 2800, "duration": "3 sem.", "difficulty": 4, "status_default": "locked", "requires": "webserv"},
            {"slug": "ft_transcendence", "name": "ft_transcendence", "description": "Le projet final : une SPA temps réel avec un Pong multijoueur en ligne.", "level": "Niveau 8", "level_value": 8.0, "lang": "Web", "lang_color": "#F5B942", "tags": ["Groupe", "Fullstack", "WebSocket"], "xp": 8000, "duration": "8 sem.", "difficulty": 5, "status_default": "locked", "requires": "inception"},
        ]
        for data in default_projects:
            if not db.query(Project).filter(Project.slug == data["slug"]).first():
                p = Project(**data)
                db.add(p)
        db.commit()
    
    # Seed demo user if empty
    if db.query(User).filter(User.username == "abdeljalil").count() == 0:
        demo = User(
            username="abdeljalil",
            email="abdeljalil@root404.tn",
            display_name="Abdeljalil",
            full_name="Abdeljalil Ben Youssef",
            campus="Tunis",
            level=6.42,
            xp=24780,
            xp_to_next=3220,
            projects_done=38,
            correction_points=1250,
            account_value=2450,
            jetons=4,
            streak=24,
            accuracy=81,
            reputation=88,
            integrity_score=96,
            bio="Étudiant en systèmes & réseaux. J'aime le C, les pointeurs et les segfaults à 3h du matin.",
            is_active=True,
            is_verified=True,
            skills=SkillGraphService.initialize_skills()
        )
        db.add(demo)
        db.commit()
        try:
            CoalitionService.assign_user_to_coalition(demo, db)
        except:
            pass

finally:
    db.close()
