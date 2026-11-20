"""Durable, bounded request claims. Never stores learner source or credentials."""
import os
from pathlib import Path
import sqlite3


class ReplayStore:
    def __init__(self,path):
        self.path=path
        Path(path).parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(path,os.O_CREAT|os.O_RDWR,0o600);os.close(fd)
        with sqlite3.connect(path,timeout=5) as db:
            db.execute('CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, created INTEGER NOT NULL)')

    def claim(self,identity,now):
        with sqlite3.connect(self.path,timeout=5,isolation_level=None) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM claims WHERE created < ?', (now-180,))
            if db.execute('SELECT count(*) FROM claims').fetchone()[0]>=10000:
                db.rollback(); raise RuntimeError('Replay claim capacity reached')
            try: db.execute('INSERT INTO claims VALUES (?,?)',(identity,now))
            except sqlite3.IntegrityError:
                db.rollback(); return False
            db.commit(); return True
