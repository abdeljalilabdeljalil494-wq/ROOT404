from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user, judge_rate_limit, ai_rate_limit
from app.models.user import User
from app.services.ai_helper import AIMentorService, detect_topic
from app.services.integrity import IntegrityService

router = APIRouter(prefix="/ai", tags=["AI Mentor"])

class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    level: int = Field(2, ge=1, le=5)
    project_slug: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=100000)

class ReviewRequest(BaseModel):
    code: str = Field(min_length=1, max_length=100000)
    project_slug: Optional[str] = Field(None, max_length=100)
    language: str = Field("c", max_length=20)

class HistoryResponse(BaseModel):
    role: str
    text: str
    list: Optional[List[str]] = None
    footer: Optional[str] = None

@router.get("/history")
def get_history(limit: int = Query(50, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.mentor import MentorInteraction
    rows = db.query(MentorInteraction).filter_by(user_id=current_user.id).order_by(
        MentorInteraction.created_at.desc(), MentorInteraction.id.desc()).limit(limit).all()
    result = []
    for interaction in reversed(rows):
        result.extend([{'role': 'user', 'text': interaction.message, 'interaction_id': interaction.id},
                       {**interaction.response, 'interaction_id': interaction.id}])
    return result

@router.post("/ask", dependencies=[Depends(judge_rate_limit), Depends(ai_rate_limit)])
def ask_ai(payload: AskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.ai_provider import ask_provider, save_interaction
    response = ask_provider(payload.message, payload.level, {'project_slug': payload.project_slug, 'code': payload.code})
    # No automatic integrity penalty from superficial paste/comment heuristics.
    return save_interaction(db, current_user.id, 'ask', payload.message, response)

@router.post("/review", dependencies=[Depends(judge_rate_limit), Depends(ai_rate_limit)])
def ai_review(payload: ReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.ai_provider import review_code
    return review_code(db, current_user.id, payload.code, payload.language, payload.project_slug)

@router.get("/levels")
def get_levels():
    return [
        {"n": 1, "label": "Hint initial", "description": "Indice léger, te pousse dans la bonne direction"},
        {"n": 2, "label": "Question socratique", "description": "Questions qui te font réfléchir par toi-même"},
        {"n": 3, "label": "Explication du concept", "description": "Explique le concept sous-jacent sans donner la solution"},
        {"n": 4, "label": "Exemple simplifié", "description": "Exemple minimal non copiable, illustre le concept"},
        {"n": 5, "label": "Ressources & exercices", "description": "Liens, man pages et micro-exercices pour approfondir"},
    ]

@router.get("/gaps")
def get_knowledge_gaps(current_user: User = Depends(get_current_user)):
    from app.services.skill_graph import SkillGraphService
    gaps = SkillGraphService.get_knowledge_gaps(current_user)
    challenges = SkillGraphService.recommend_micro_challenges(gaps)
    return {"gaps": gaps, "challenges": challenges}

@router.post("/detect-cheating")
def detect_cheating(payload: ReviewRequest, current_user: User = Depends(get_current_user)):
    result = AIMentorService.detect_cheating(payload.code, [])
    return {**result, "method": "lexical_heuristic", "proof_of_cheating": False}
