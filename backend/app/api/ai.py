"""AI Mentor endpoints.

    GET  /ai/history   {messages, context, stats} — conversation persistée
    POST /ai/ask       {message, level?} → réponse socratique (jamais la solution)
    GET  /ai/review    {metrics, notes}  — AI Code Review sur la dernière soumission
    POST /ai/reset     nouvelle conversation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session

from .. import models
from ..core.db import get_db
from ..core.security import get_current_user
from ..schemas import AskIn
from ..services import ai as ai_svc

router = APIRouter()


@router.get("/history")
def history(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ai_svc.history_payload(db, user)


@router.post("/ask")
def ask(
    body: AskIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message vide.")
    if len(message) > 2000:
        raise HTTPException(status_code=400, detail="Message trop long (2000 caractères max).")
    return ai_svc.ask_payload(db, user, message, body.level)


@router.get("/review")
def review(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ai_svc.review_payload(db, user)


@router.post("/reset")
def reset(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(delete(models.AiMessage).where(models.AiMessage.user_id == user.id))
    db.commit()
    return {"ok": True}
