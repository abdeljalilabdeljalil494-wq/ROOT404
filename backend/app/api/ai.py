from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.ai_helper import AIMentorService, get_socratic_hint, analyze_code_review, detect_topic
from app.services.integrity import IntegrityService

router = APIRouter(prefix="/ai", tags=["AI Mentor"])

class AskRequest(BaseModel):
    message: str
    level: int = 2
    project_slug: Optional[str] = None
    code: Optional[str] = None

class ReviewRequest(BaseModel):
    code: str
    project_slug: Optional[str] = None
    language: str = "c"

class HistoryResponse(BaseModel):
    role: str
    text: str
    list: Optional[List[str]] = None
    footer: Optional[str] = None

@router.get("/history")
def get_history(current_user: User = Depends(get_current_user)):
    # Mock history - in production would be from DB
    return [
        {
            "role": "ai",
            "text": "Salut 👋 J'ai analysé ta dernière soumission de `minishell`. Je ne vais pas te donner la solution — mais je peux t'aider à la trouver. Par quoi veux-tu commencer ?",
            "chips": ["Comprendre mon erreur", "Expliquer un concept", "Me donner un indice"]
        },
        {
            "role": "user",
            "text": "Mon shell segfault quand je fais `cat | cat | ls`. Je ne comprends pas pourquoi."
        },
        {
            "role": "ai",
            "text": "Bonne observation — ce cas enchaîne trois processus. Avant de plonger dans le code, réponds-moi :",
            "list": [
                "Combien de pipes crées-tu pour 3 commandes ?",
                "Que deviennent les descripteurs dans le processus parent après le fork ?",
                "Est-ce que chaque enfant ferme bien les extrémités qu'il n'utilise pas ?"
            ],
            "footer": "Un segfault ici vient souvent d'un `close()` manquant ou d'un tableau de pipes mal indexé."
        }
    ]

@router.post("/ask")
def ask_ai(payload: AskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Detect cheating
    if payload.code:
        cheating = AIMentorService.detect_cheating(payload.code, [])
        if cheating["is_suspicious"]:
            IntegrityService.log_action(
                current_user.id, "ai_cheating_flag", "ai", None,
                {"flags": cheating["flags"], "question": payload.message[:100]}, db=db
            )
    
    context = {"project_slug": payload.project_slug}
    response = AIMentorService.ask(payload.message, payload.level, context)
    
    # Log AI interaction for integrity score
    IntegrityService.log_action(
        current_user.id, "ai_ask", "ai", None,
        {"level": payload.level, "topic": detect_topic(payload.message), "project": payload.project_slug}, db=db
    )
    
    return response

@router.post("/review")
def ai_review(payload: ReviewRequest, current_user: User = Depends(get_current_user)):
    result = analyze_code_review(payload.code, payload.project_slug)
    return result

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
    return result
