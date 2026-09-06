"""Dev seed — mirrors frontend/src/data/mock.js so the real API serves the
same domain the UI was designed on. Runs once on startup when the DB is empty.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from .. import models
from ..core.db import SessionLocal

# (name, color, points, members, wins, trend, motto)
COALITIONS = [
    ("The Phoenix", "#F8851F", 7286, 312, 14, "+320", "Renaître de chaque segfault."),
    ("Neon Wolves", "#3B9EFF", 6941, 298, 11, "+180", "La meute compile ensemble."),
    ("Data Vipers", "#2ECC71", 6402, 305, 9, "+95", "Silencieux, précis, mortels."),
    ("Sand Foxes", "#F5B942", 5877, 281, 8, "+60", "Rusés dans le désert du code."),
]

# (id, slug, name, level, lang, color, desc, tags, xp, duration, difficulty, requires)
PROJECTS = [
    ("p1", "get_next_line", "get_next_line", "Niveau 1", "C", "#3B9EFF",
     "Lis une ligne depuis un file descriptor, sans jamais perdre le fil.",
     ["Solo", "I/O", "Buffer"], 1200, "1 sem.", 2, None),
    ("p2", "ft_printf", "ft_printf", "Niveau 2", "C", "#3B9EFF",
     "Recode la fonction variadique la plus utilisée de la libc.",
     ["Solo", "Variadic", "Parsing"], 1500, "2 sem.", 3, None),
    ("p3", "minishell", "minishell", "Niveau 4", "C", "#3B9EFF",
     "Écris ton propre shell : parsing, pipes, redirections, builtins et signaux.",
     ["Duo", "Unix", "Parsing"], 3200, "4 sem.", 5, None),
    ("p4", "philosophers", "philosophers", "Niveau 3", "C", "#3B9EFF",
     "Résous le problème des philosophes avec threads et mutex, sans data race.",
     ["Solo", "Threads", "Concurrence"], 2100, "2 sem.", 4, None),
    ("p5", "netpractice", "netpractice", "Niveau 4", "Réseau", "#2ECC71",
     "Configure des réseaux TCP/IP et comprends enfin le masque de sous-réseau.",
     ["Solo", "Réseau"], 1100, "3 j.", 2, None),
    ("p6", "cub3d", "cub3d", "Niveau 5", "C", "#3B9EFF",
     "Un moteur de rendu 3D en raycasting, inspiré du légendaire Wolfenstein 3D.",
     ["Duo", "Graphique", "Maths"], 3600, "4 sem.", 5, None),
    ("p7", "webserv", "webserv", "Niveau 6", "C++", "#F26FA4",
     "Implémente un serveur HTTP/1.1 conforme, non-bloquant, façon NGINX.",
     ["Trio", "Réseau", "HTTP"], 4200, "5 sem.", 5, "minishell"),
    ("p8", "inception", "inception", "Niveau 6", "Docker", "#3B9EFF",
     "Orchestre une infrastructure multi-conteneurs avec Docker Compose.",
     ["Solo", "DevOps", "Docker"], 2800, "3 sem.", 4, "webserv"),
    ("p9", "ft_transcendence", "ft_transcendence", "Niveau 8", "Web", "#F5B942",
     "Le projet final : une SPA temps réel avec un Pong multijoueur en ligne.",
     ["Groupe", "Fullstack", "WebSocket"], 8000, "8 sem.", 5, "inception"),
]

# The demo student — mirrors mock.currentUser
MAIN_STUDENT = dict(
    username="abdeljalil",
    email="abdeljalil@root404.tn",
    display_name="Abdeljalil",
    full_name="Abdeljalil Ben Youssef",
    title="Coder — Cursus Systèmes",
    campus="Tunis",
    avatar="https://i.pravatar.cc/160?img=13",
    bio="Étudiant en systèmes & réseaux. J'aime le C, les pointeurs et les segfaults à 3h du matin.",
    github="abdeljalil", discord="abdeljalil#404", site="root404.tn/u/abdeljalil",
    level=6.42, level_progress=42, xp=24780, xp_to_next=3220, projects_done=38,
    correction_points=1250, account_value=2450, jetons=4, streak=24,
    accuracy=81, reputation=88, integrity=96,
    blackhole_days_left=87, blackhole_total=120,
    joined="Sept. 2025",
)

# A few more students so the leaderboard step has real data (mirrors mock.leaderboard)
OTHER_STUDENTS = [
    ("blackholesurvivor", "Yassine Trabelsi", "Yassine T.", 11.36, 58420, 64, 93, 0, 12),
    ("chaimacoder", "Chaima Ben Ali", "Chaima B.", 10.87, 51110, 60, 91, 1, 45),
    ("mehdi42", "Mehdi Karray", "Mehdi K.", 9.94, 46230, 52, 90, 2, 33),
    ("ines_dev", "Ines Sayeh", "Ines S.", 6.36, 23940, 37, 89, 1, 47),
    ("skhalifa", "Sarra Khalifa", "Sarra K.", 6.02, 22180, 35, 86, 3, 26),
    ("nour_dev", "Nour Haddad", "Nour H.", 5.88, 21050, 33, 84, 2, 32),
    ("oussama_c", "Oussama Riachi", "Oussama R.", 5.41, 19620, 31, 79, 0, 53),
]

# (slug, status, score, bonus, progress, retry_days)
MAIN_USER_PROJECTS = [
    ("get_next_line", "done", 100, False, 100, 0),
    ("ft_printf", "done", 115, True, 100, 0),
    ("minishell", "progress", None, False, 68, 0),
    ("philosophers", "failed", 42, False, 0, 2),
    ("netpractice", "done", 100, False, 100, 0),
]

# (slug, kind, score, tone, xp, hours_ago)
MAIN_ACTIVITY = [
    ("get_next_line", "Moulinette réussie", "100", "ok", 1200, 2),
    ("ft_printf", "Peer Review validé", "115", "ok", 0, 5),
    ("minishell", "Soumission en attente", "En cours", "brand", 0, 22),
    ("netpractice", "Niveau validé", "100", "ok", 1100, 72),
    ("philosophers", "Moulinette échouée", "42", "danger", 0, 96),
]

# Daily missions across the last 7 days (feed the weekly activity chart)
DAILY_MISSION_XP = [540, 780, 880, 310, 420, 680, 950]  # 6 days ago → today


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _main_user(db) -> models.User:
    q = select(models.User).where(models.User.email == MAIN_STUDENT["email"])
    return db.execute(q).scalar_one_or_none()


def seed_if_empty() -> bool:
    """Seed the DB with the demo dataset. Returns True when it seeded."""
    db = SessionLocal()
    try:
        if db.execute(select(models.User).limit(1)).scalar_one_or_none() is not None:
            return False

        # --- Coalitions -------------------------------------------------
        coalitions: dict[str, models.Coalition] = {}
        for i, (name, color, points, members, wins, trend, motto) in enumerate(COALITIONS):
            c = models.Coalition(
                id=f"c_{i + 1:03d}", name=name, color=color, points=points,
                members=members, wins=wins, trend=trend, motto=motto,
            )
            db.add(c)
            coalitions[name] = c
        db.flush()

        # --- Projects ----------------------------------------------------
        projects: dict[str, models.Project] = {}
        for i, (pid, slug, name, level, lang, color, desc, tags, xp, dur, diff, req) in enumerate(PROJECTS):
            p = models.Project(
                id=pid, slug=slug, name=name, level_label=level, lang=lang,
                lang_color=color, description=desc, tags=tags, xp=xp,
                duration=dur, difficulty=diff, requires=req, order=i,
            )
            db.add(p)
            projects[slug] = p
        db.flush()

        # --- Main student -------------------------------------------------
        main = models.User(
            id="u_001",
            coalition_id=coalitions["The Phoenix"].id,
            **MAIN_STUDENT,
        )
        db.add(main)
        db.flush()

        # --- Main student's project states --------------------------------
        for slug, status, score, bonus, progress, retry_days in MAIN_USER_PROJECTS:
            up = models.UserProject(
                user_id=main.id,
                project_id=projects[slug].id,
                status=status,
                score=score,
                bonus=bonus,
                progress=progress,
                retry_after=_now() + timedelta(days=retry_days) if retry_days else None,
            )
            db.add(up)

        # --- Activity feed --------------------------------------------------
        now = _now()
        for slug, kind, score, tone, xp, hours_ago in MAIN_ACTIVITY:
            db.add(models.ActivityEvent(
                user_id=main.id, project=slug, kind=kind, score=score,
                tone=tone, xp=xp, created_at=now - timedelta(hours=hours_ago),
            ))
        for i, xp in enumerate(DAILY_MISSION_XP):  # i = 0 → 6 days ago, last → today
            db.add(models.ActivityEvent(
                user_id=main.id, project="daily-mission",
                kind="Mission quotidienne", score=str(xp), tone="ok",
                xp=xp, created_at=now - timedelta(days=6 - i, hours=3),
            ))

        # --- A few past submissions (history) ------------------------------
        sub_specs = [
            ("get_next_line", "passed", 100, 48),
            ("ft_printf", "passed", 115, 70),
            ("philosophers", "failed", 42, 96),
            ("minishell", "pending", None, 22),
        ]
        for i, (slug, status, score, hours_ago) in enumerate(sub_specs):
            db.add(models.Submission(
                id=f"s_{i + 1:03d}",
                user_id=main.id,
                project_id=projects[slug].id,
                files=[{"path": "src/main.c", "content": "// seed history"}],
                status=status,
                score=score,
                created_at=now - timedelta(hours=hours_ago),
            ))

        # --- Other students --------------------------------------------------
        for i, (username, full, display, level, xp, done, acc, co_idx, img) in enumerate(OTHER_STUDENTS):
            db.add(models.User(
                id=f"u_{i + 2:03d}",
                username=username,
                email=f"{username}@root404.tn",
                display_name=display,
                full_name=full,
                title="Coder — Cursus C",
                campus="Tunis",
                avatar=f"https://i.pravatar.cc/160?img={img}",
                level=level,
                level_progress=(level * 7) % 100,
                xp=xp,
                xp_to_next=500,
                projects_done=done,
                accuracy=acc,
                reputation=80 + (i * 3) % 20,
                integrity=95,
                blackhole_days_left=60 + i * 7,
                blackhole_total=120,
                joined="Sept. 2025",
                coalition_id=coalitions[list(coalitions)[co_idx]].id,
                github=username,
                discord=f"{username}#404",
                site=f"root404.tn/u/{username}",
            ))

        db.commit()
        return True
    finally:
        db.close()
