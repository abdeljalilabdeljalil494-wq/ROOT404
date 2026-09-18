from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional
import re
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_user, judge_rate_limit
from app.core.security import sanitize_input
from app.core.config import settings
from app.models.user import User
from app.services.judge import run_moulinette, run_code_in_sandbox, JudgeService, validate_files
from app.services.ai_helper import analyze_code_review

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/judge", tags=["Judge / Moulinette"])

class RunRequest(BaseModel):
    project_slug: str = Field(..., max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    files: Dict[str, str] = Field(..., description="Filename to content map")
    language: str = Field("c", max_length=20, pattern=r'^[a-zA-Z0-9\+\#]+$')
    
    @field_validator('files')
    @classmethod
    def validate_files_field(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Files required")
        if len(v) > settings.JUDGE_MAX_FILES:
            raise ValueError(f"Too many files, max {settings.JUDGE_MAX_FILES}")
        total = 0
        for fname, content in v.items():
            if len(fname) > 100 or ".." in fname or fname.startswith("/") or "\x00" in fname:
                raise ValueError(f"Invalid filename: {fname}")
            total += len(content.encode('utf-8'))
            if total > settings.JUDGE_MAX_TOTAL_SIZE:
                raise ValueError("Total size too large")
        return v

class CodeRunRequest(BaseModel):
    code: str = Field(..., max_length=100000, description="Code to run")
    language: str = Field("c", max_length=20, pattern=r'^[a-zA-Z0-9\+\#]+$')
    test_input: str = Field("", max_length=10240)
    
    @field_validator('code')
    @classmethod
    def sanitize_code(cls, v):
        if "\x00" in v:
            raise ValueError("Null bytes not allowed")
        return v

class PlagiarismRequest(BaseModel):
    code1: str = Field(..., max_length=100000)
    code2: str = Field(..., max_length=100000)

@router.post("/run", dependencies=[Depends(judge_rate_limit)])
def run_code(payload: CodeRunRequest, request: Request, current_user: User = Depends(get_current_user)):
    try:
        language = sanitize_input(payload.language, max_length=20).lower()
        if language not in ["c", "cpp", "c++", "python", "py", "javascript", "js"]:
            raise HTTPException(status_code=400, detail="Unsupported language")
        
        result = run_code_in_sandbox(payload.code, language, payload.test_input[:10240])
        logger.info(f"Judge run by {current_user.username} - lang={language} - status={result.get('status')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Judge run failed for {current_user.username}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Execution failed")

@router.post("/moulinette/{slug}", dependencies=[Depends(judge_rate_limit)])
def moulinette(slug: str, payload: RunRequest, request: Request, current_user: User = Depends(get_current_user)):
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        raise HTTPException(status_code=400, detail="Invalid project slug")
    
    valid, msg = validate_files(payload.files, payload.language)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    
    try:
        result = run_moulinette(slug, payload.files, payload.language)
        logger.info(f"Moulinette {slug} by {current_user.username} - score={result.get('score')}")
        return result
    except Exception as e:
        logger.error(f"Moulinette failed for {slug}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Moulinette failed")

@router.post("/review", dependencies=[Depends(judge_rate_limit)])
def code_review(payload: CodeRunRequest, current_user: User = Depends(get_current_user)):
    try:
        if len(payload.code) > 100000:
            raise HTTPException(status_code=400, detail="Code too large")
        review = analyze_code_review(payload.code, None)
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code review failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Review failed")

@router.post("/plagiarism")
def check_plagiarism(payload: PlagiarismRequest, current_user: User = Depends(get_current_user)):
    try:
        score = JudgeService.check_plagiarism(payload.code1, payload.code2)
        return {"similarity": score}
    except Exception as e:
        logger.error(f"Plagiarism check failed: {e}")
        raise HTTPException(status_code=500, detail="Plagiarism check failed")

@router.post("/complexity")
def analyze_complexity(payload: CodeRunRequest, current_user: User = Depends(get_current_user)):
    try:
        analysis = JudgeService.analyze_complexity(payload.code)
        return analysis
    except Exception as e:
        logger.error(f"Complexity analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.get("/runners")
def list_runners(current_user: User = Depends(get_current_user)):
    return {
        "runners": [
            {"language": "c", "image": "gcc:12", "enabled": True, "version": "12.2", "hardened": True},
            {"language": "c++", "image": "gcc:12", "enabled": True, "version": "12.2", "hardened": True},
            {"language": "python", "image": "python:3.11-slim", "enabled": True, "version": "3.11", "hardened": True},
            {"language": "javascript", "image": "node:20-slim", "enabled": True, "version": "20", "hardened": True},
            {"language": "rust", "image": "rust:1.75", "enabled": False, "version": "1.75"},
            {"language": "go", "image": "golang:1.21", "enabled": False, "version": "1.21"},
        ],
        "isolation": {
            "network": "none",
            "memory_limit": settings.JUDGE_MEMORY_LIMIT,
            "cpu_limit": str(settings.JUDGE_CPU_LIMIT),
            "timeout": settings.JUDGE_TIMEOUT,
            "pids_limit": 64,
            "read_only_rootfs": True,
            "no_new_privileges": True,
            "seccomp": True,
            "cap_drop": "ALL"
        },
        "security": {
            "forbidden_patterns": True,
            "path_traversal_protection": True,
            "file_size_limits": True,
            "output_truncation": True
        }
    }
