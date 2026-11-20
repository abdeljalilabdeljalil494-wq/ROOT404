"""Read-only grading inventory. Never fabricates specs, test executions or passes."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.services.grading_contracts import ORIGINAL_PROJECTS, original_eligibility


def main():
    rows=[original_eligibility(slug) for slug in ORIGINAL_PROJECTS]
    print(json.dumps({'status':'INCOMPLETE','source':'backend/app/api/projects.py:seed_projects',
                      'note':'Versioned authoritative subjects absent; nine complete trusted harnesses not implemented.',
                      'projects':rows},indent=2))
    return 1


if __name__=='__main__': raise SystemExit(main())
