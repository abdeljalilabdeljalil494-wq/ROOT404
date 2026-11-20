"""Unprivileged input loader, NOT a supervisor or result authority.

Exec replaces this process. It emits no execution metadata. The host observes
Docker exit/OOM state independently. No secrets/expected answers enter this image.
"""
import json
import math
import os
from pathlib import Path
import re
import resource
import sys
import tempfile


def main():
    if os.getuid()!=1000 or os.getgid()!=1000:
        raise RuntimeError('Non-root learner identity required')
    status = dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    if any(int(status[key].strip(),16) for key in ['CapEff','CapPrm','CapInh','CapAmb']):
        raise RuntimeError('Learner capabilities forbidden')
    if status['NoNewPrivs'].strip()!='1':
        raise RuntimeError('no-new-privileges required')
    raw = sys.stdin.buffer.read(1048577)
    if len(raw)>1048576: raise ValueError('Job too large')
    job = json.loads(raw)
    language = {'c++':'cpp','py':'python','js':'javascript'}.get(job['language'],job['language'])
    if language not in {'c','cpp','python','javascript'}: raise ValueError('Language')
    phase = sys.argv[1]
    if phase not in {'compile','run'}: raise ValueError('Phase')
    root = Path('/workspace')
    files = job['files']
    if not isinstance(files,dict) or not 1<=len(files)<=20: raise ValueError('Files')
    total = 0
    for name,source in files.items():
        if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]{0,99}',name) or any(
            part in {'','.','..'} or part.startswith('.') for part in name.split('/')):
            raise ValueError('Filename')
        if not isinstance(source,str) or '\0' in source or len(source.encode())>262144: raise ValueError('Source')
        total += len(source.encode())
    if total>524288: raise ValueError('Sources too large')
    # Do not rewrite compiler artifacts or source between compile and run.
    if phase=='compile' or language in {'python','javascript'}:
        for name,source in files.items():
            target = root/name
            target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            target.write_text(source); target.chmod(0o600)
    timeout = job['timeout_seconds']
    if type(timeout) is not int or not 1<=timeout<=30: raise ValueError('Timeout')
    for limit,soft,hard in [(resource.RLIMIT_CORE,0,0),(resource.RLIMIT_NPROC,48,48),
        (resource.RLIMIT_CPU,math.ceil(timeout),math.ceil(timeout)+1),
        (resource.RLIMIT_FSIZE,32*1024*1024,32*1024*1024),(resource.RLIMIT_NOFILE,64,64),
        (resource.RLIMIT_AS,(1024 if language=='javascript' else 512)*1024*1024,
                          (1024 if language=='javascript' else 512)*1024*1024)]:
        resource.setrlimit(limit,(soft,hard))
    suffixes = {'c':('.c',),'cpp':('.cpp','.cc')}
    if phase=='compile':
        if language not in suffixes: raise ValueError('Compilation language')
        sources = [str(root/name) for name in sorted(files) if name.endswith(suffixes[language])]
        if not sources: raise ValueError('No sources')
        command = ['/usr/bin/gcc' if language=='c' else '/usr/bin/g++','-Wall','-Wextra','-Werror',
                   '-I',str(root),*sources,'-o',str(root/'.root404-program')]
    elif language in {'c','cpp'}:
        command = [str(root/'.root404-program')]
    else:
        extension = '.py' if language=='python' else '.js'
        candidates = sorted(name for name in files if name.endswith(extension))
        main = 'main'+extension
        if main not in candidates:
            if len(candidates)!=1: raise ValueError('Main required')
            main = candidates[0]
        command = ['/usr/bin/python3','-I',str(root/main)] if language=='python' else [
            '/usr/bin/node','--jitless','--max-old-space-size=64',str(root/main)]
    stdin = job.get('stdin','') if phase=='run' else ''
    if len(stdin.encode())>10240: raise ValueError('Input too large')
    with tempfile.TemporaryFile(dir='/tmp') as incoming:
        incoming.write(stdin.encode()); incoming.seek(0)
        os.dup2(incoming.fileno(),0)
    os.chdir(root)
    os.execve(command[0],command,{'PATH':'/usr/bin:/bin','HOME':str(root),'TMPDIR':'/tmp','LANG':'C.UTF-8'})


if __name__=='__main__': main()
