"""Administrative CLI; run only with trusted deployment access."""
import argparse
from datetime import datetime
from app.core.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['seed-catalog', 'cleanup-auth', 'retention', 'seed-execution-projects', 'set-admin'])
    parser.add_argument("--apply", action="store_true", help="Apply retention deletion; default is dry-run")
    args = parser.parse_args()
    with SessionLocal() as db:
        if args.command == 'set-admin':
            import os
            set_admin(db,os.environ.get('ROOT404_ADMIN_EMAIL',''),os.environ.get('ROOT404_ADMIN_ROLE',''))
            print('Administrator role updated; target sessions revoked. No account created.')
        elif args.command == 'seed-catalog':
            from app.api.projects import seed_projects
            seed_projects(db)
            print('Project catalog seeded idempotently; no users or progress created. Executable suites still require configuration.')
        elif args.command == 'retention':
            from app.services.retention import purge_expired
            print(purge_expired(db, apply=args.apply))
        elif args.command == 'seed-execution-projects':
            from app.services.project_suites import seed_execution_projects
            print(seed_execution_projects(db))
        else:
            from app.models.auth_state import OTPChallenge, AuthThrottle, RevokedToken
            now = datetime.utcnow()
            for model in (OTPChallenge, AuthThrottle, RevokedToken):
                db.query(model).filter(model.expires_at <= now).delete()
            db.commit()
            print('Expired authentication state removed.')


def set_admin(db,email,role):
    """Trusted host CLI ONLY. Never reachable through registration/public API."""
    import os
    from app.models.user import User
    if os.environ.get('ROOT404_ALLOW_ADMIN_CHANGE')!='yes' or role not in {'grant','revoke'}:
        raise ValueError('Explicit operator role-change consent and grant/revoke required')
    user=db.query(User).filter(User.email==email.lower().strip(),User.is_active==True,
        User.is_verified==True).with_for_update().first()
    if not user: raise ValueError('Existing active verified target required')
    user.is_admin=role=='grant'
    user.session_version+=1
    db.commit()


if __name__ == '__main__':
    main()
