"""Run an operator check, preserve exit status, and save redacted reports.

Never loads .env. Do not pass secrets as command arguments. Environment secrets
are inherited only by the child; no environment/command snapshot is recorded.
"""
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import shutil
import sys


def redact(text):
    for key,value in os.environ.items():
        if value and len(value)>=4 and re.search(r'SECRET|TOKEN|PASSWORD|API_KEY|DSN|DATABASE_URL|REDIS_URL',key,re.I):
            text=text.replace(value,'[REDACTED]')
    text=re.sub(r'(?i)(authorization\s*[:=]\s*)(?:bearer\s+)?[^\s,]+',r'\1[REDACTED]',text)
    return re.sub(r'(\w+://)[^\s/@]+:[^\s/@]+@',r'\1[REDACTED]@',text)


def main():
    if len(sys.argv)<3: raise SystemExit('Usage: report_run.py NAME COMMAND [ARGS]')
    name=sys.argv[1]
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',name): raise SystemExit('Invalid report name')
    root=Path(__file__).resolve().parents[1]; directory=root/'reports'; directory.mkdir(mode=0o700,exist_ok=True)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    code=1
    with (directory/f'{name}.log').open('w') as output:
        os.chmod(output.name,0o600)
        try:
            child=subprocess.Popen(sys.argv[2:],cwd=root,env=dict(os.environ,ROOT404_REPORT_ACTIVE='yes'),
                                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
            for line in child.stdout:
                line=redact(line); output.write(line); output.flush(); print(line,end='',flush=True)
            code=child.wait()
        except (OSError,KeyboardInterrupt) as error:
            if 'child' in locals() and child.poll() is None:
                child.terminate(); child.wait(timeout=15)
            output.write(f'Runner failed: {type(error).__name__}\n')
        finally:
            if name in {'test-judge','test-judge-docker-ci','test-judge-linux'}:
                source=root/'.cache/judge-results'
                target=directory/'judge-isolation'
                if target.exists(): shutil.rmtree(target)
                target.mkdir(exist_ok=True,mode=0o700)
                if source.exists():
                    for path in source.rglob('*'):
                        if path.is_file() and path.suffix in {'.json','.txt','.log'} and path.stat().st_size<=4*1024*1024:
                            destination=target/path.relative_to(source); destination.parent.mkdir(parents=True,exist_ok=True)
                            destination.write_text(redact(path.read_text(errors='replace'))); destination.chmod(0o600)
            summary={'check':name,'started_at':start,'exit_code':code,'result':'PASS' if code==0 else 'NOT_PASSED',
                     'scope':'Command exit only; inspect gate-specific evidence. Not production authorization.'}
            path=directory/f'{name}.json'; path.write_text(json.dumps(summary,indent=2)); path.chmod(0o600)
    return code if code>=0 else 1


if __name__=='__main__': raise SystemExit(main())
