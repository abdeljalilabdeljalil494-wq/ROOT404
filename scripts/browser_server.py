"""Disposable browser-test backend. No existing DB, SMTP or auth bypass.

Development OTP comes from the real API only in this isolated process. This is
browser integration evidence, never production mail/PostgreSQL evidence.
"""
import os
from pathlib import Path
import secrets
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
with tempfile.TemporaryDirectory(prefix='root404-browser-') as directory:
    os.environ.update(DATABASE_URL='sqlite:///'+directory+'/browser.db', ENVIRONMENT='development',
                      EMAIL_PROVIDER='development', ENABLE_DEV_OTP='true', SECRET_KEY=secrets.token_hex(32), SEED_DEMO_DATA='false',
                      ENABLE_DEMO_FEATURES='false', JUDGE_ENABLED='false', AI_PROVIDER='disabled',
                      RATE_LIMIT_AUTH_REQUESTS='200', OTP_RATE_LIMIT_PER_HOUR='30', REDIS_URL='')
    from app.core.database import init_db,SessionLocal
    from app.models.user import User
    from app.models.submission import Submission
    from app.models.project import Project
    from app.services.project_suites import seed_execution_projects
    init_db()
    with SessionLocal() as db:
        for name in ['desktop','tablet','mobile']:
            db.add(User(username='browser_'+name,email=name+'@example.com',display_name='Browser '+name,is_verified=True))
            db.add(User(username='moderator_'+name,email='moderator_'+name+'@example.com',display_name='Moderator '+name,is_verified=True,is_admin=True))
        seed_execution_projects(db)
        db.flush()
        project=db.query(Project).filter_by(slug='foundations-sum-python').one()
        for name in ['desktop','tablet','mobile']:
            # Explicit browser fixture, NOT a claimed judge execution result.
            author=db.query(User).filter_by(email=name+'@example.com').one()
            db.add(Submission(user_id=author.id,project_id=project.id,
                files={'main.py':'print(0)'},status='failed',score=0))
            db.add(User(username='reviewer_'+name,email='reviewer_'+name+'@example.com',
                display_name='Reviewer '+name,is_verified=True))
        db.commit()
    import uvicorn
    uvicorn.run('app.main:app',host='0.0.0.0',port=8011,access_log=False)
