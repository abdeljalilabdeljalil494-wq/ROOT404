"""Fresh initialization and a data-preserving incremental SQLite upgrade."""
import os
from pathlib import Path
import subprocess
import sys
from sqlalchemy import create_engine, inspect, text


def test_fresh_migrations_and_upgrade_preserve_existing_data(tmp_path):
    root = Path(__file__).resolve().parents[2]
    url = 'sqlite:///' + str(tmp_path / 'migrations.db')
    env = dict(os.environ, DATABASE_URL=url, ENVIRONMENT='development')
    command = [sys.executable, '-m', 'alembic', '-c', str(root / 'backend/alembic.ini')]
    subprocess.run(command + ['upgrade', '0001'], env=env, cwd=root, check=True, capture_output=True)
    engine = create_engine(url)
    # A real existing row in a baseline table, not a new empty migration only.
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO badges (id,name,icon,tier,criteria) VALUES ('keep','Keep me','Star','bronze','{}')"))
    subprocess.run(command + ['upgrade', 'head'], env=env, cwd=root, check=True, capture_output=True)
    assert {'oauth_identities', 'oauth_attempts', 'otp_challenges', 'auth_throttles', 'revoked_tokens', 'mentor_interactions'} <= set(inspect(engine).get_table_names())
    with engine.connect() as conn:
        assert conn.execute(text("SELECT name FROM badges WHERE id='keep'")).scalar_one() == 'Keep me'
        assert conn.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '0007'
    subprocess.run(command + ['downgrade', '0001'], env=env, cwd=root, check=True, capture_output=True)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT name FROM badges WHERE id='keep'")).scalar_one() == 'Keep me'
    subprocess.run(command + ['upgrade', 'head'], env=env, cwd=root, check=True, capture_output=True)
