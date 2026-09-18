from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.judge import run_moulinette, run_code_in_sandbox, JudgeService
from app.services.ai_helper import analyze_code_review

router = APIRouter(prefix="/judge", tags=["Judge / Moulinette"])

class RunRequest(BaseModel):
    project_slug: str
    files: Dict[str, str]
    language: str = "c"

class CodeRunRequest(BaseModel):
    code: str
    language: str = "c"
    test_input: str = ""

class PlagiarismRequest(BaseModel):
    code1: str
    code2: str

@router.post("/run")
def run_code(payload: CodeRunRequest, current_user: User = Depends(get_current_user)):
    result = run_code_in_sandbox(payload.code, payload.language, payload.test_input)
    return result

@router.post("/moulinette/{slug}")
def moulinette(slug: str, payload: RunRequest, current_user: User = Depends(get_current_user)):
    result = run_moulinette(slug, payload.files, payload.language)
    return result

@router.post("/review")
def code_review(payload: CodeRunRequest, current_user: User = Depends(get_current_user)):
    review = analyze_code_review(payload.code, None)
    return review

@router.post("/plagiarism")
def check_plagiarism(payload: PlagiarismRequest, current_user: User = Depends(get_current_user)):
    score = JudgeService.check_plagiarism(payload.code1, payload.code2)
    return {"similarity": score}

@router.post("/complexity")
def analyze_complexity(payload: CodeRunRequest, current_user: User = Depends(get_current_user)):
    analysis = JudgeService.analyze_complexity(payload.code)
    return analysis

@router.get("/runners")
def list_runners():
    return {
        "runners": [
            {"language": "c", "image": "gcc:12", "enabled": True, "version": "12.2"},
            {"language": "c++", "image": "gcc:12", "enabled": True, "version": "12.2"},
            {"language": "python", "image": "python:3.11-slim", "enabled": True, "version": "3.11"},
            {"language": "javascript", "image": "node:20-slim", "enabled": True, "version": "20"},
            {"language": "rust", "image": "rust:1.75", "enabled": False, "version": "1.75"},
            {"language": "go", "image": "golang:1.21", "enabled": False, "version": "1.21"},
        ],
        "isolation": {
            "network": "none",
            "memory_limit": "512m",
            "cpu_limit": "1.0",
            "timeout": 30,
            "pids_limit": 64
        }
    }
