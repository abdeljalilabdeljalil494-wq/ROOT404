from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/exam", tags=["Exam Mode"])

EXAM_POOL = {
    "c": [
        {"id": "e1", "title": "ft_split", "difficulty": 2, "time": 30, "desc": "Découpe une chaîne selon un charset"},
        {"id": "e2", "title": "ft_atoi_base", "difficulty": 3, "time": 45, "desc": "Convertis une chaîne dans une base donnée"},
        {"id": "e3", "title": "rostring", "difficulty": 1, "time": 20, "desc": "Fais tourner les mots d'une phrase"},
        {"id": "e4", "title": "brainfuck", "difficulty": 4, "time": 60, "desc": "Interprète du brainfuck"},
    ],
    "algo": [
        {"id": "a1", "title": "Binary Search", "difficulty": 2, "time": 20},
        {"id": "a2", "title": "LRU Cache", "difficulty": 4, "time": 45},
    ]
}

class StartExamRequest(BaseModel):
    track: str = "c"
    level: int = 1

class SubmitExamRequest(BaseModel):
    exam_id: str
    files: dict
    language: str = "c"

@router.get("/tracks")
def get_tracks():
    return [
        {"id": "c", "name": "C Programming", "exams": 24, "next_gate": "Level 3.00"},
        {"id": "algo", "name": "Algorithms", "exams": 18, "next_gate": "Level 5.00"},
        {"id": "system", "name": "Systems", "exams": 15, "next_gate": "Level 7.00"},
    ]

@router.post("/start")
def start_exam(payload: StartExamRequest, current_user: User = Depends(get_current_user)):
    pool = EXAM_POOL.get(payload.track, EXAM_POOL["c"])
    # Randomly pick 3-5 exercises for exam
    selected = random.sample(pool, min(4, len(pool)))
    
    exam_id = f"exam_{random.randint(1000,9999)}"
    return {
        "exam_id": exam_id,
        "track": payload.track,
        "exercises": selected,
        "duration_minutes": sum(e["time"] for e in selected),
        "rules": [
            "Environnement isolé, pas d'accès internet",
            "Copier-coller externe désactivé",
            "Correction peer obligatoire après l'exam",
            "Pas d'assistant IA pendant l'exam"
        ],
        "starts_at": datetime.utcnow().isoformat(),
        "ends_at": (datetime.utcnow() + timedelta(minutes=sum(e["time"] for e in selected))).isoformat(),
        "status": "in_progress"
    }

@router.post("/submit")
def submit_exam(payload: SubmitExamRequest, current_user: User = Depends(get_current_user)):
    # Simulate exam grading
    score = random.randint(60, 100)
    return {
        "exam_id": payload.exam_id,
        "score": score,
        "passed": score >= 75,
        "next_step": "Réserve un slot de correction pour valider",
        "feedback": "Bon travail sur la gestion mémoire, revois les cas limites pour ft_split"
    }

@router.get("/history")
def exam_history(current_user: User = Depends(get_current_user)):
    return [
        {"id": "exam_123", "track": "C", "date": "2026-08-15", "score": 85, "passed": True},
        {"id": "exam_124", "track": "Algo", "date": "2026-08-20", "score": 92, "passed": True},
    ]

@router.get("/gates")
def get_gates(current_user: User = Depends(get_current_user)):
    return [
        {"level": "3.00", "track": "C", "status": "passed", "exam_id": "exam_123"},
        {"level": "5.00", "track": "Algo", "status": "available", "exam_id": None},
        {"level": "7.00", "track": "Systems", "status": "locked", "exam_id": None},
    ]
