"""Auth — e-mail OTP + JWT (no passwords, per the platform design).

Endpoints (contract from frontend/src/services/api.js):
    POST /auth/otp       {email}                → {sent, email[, dev_code]}
    POST /auth/verify    {email, code}          → {token, user}
    POST /auth/register  {full_name, email, …}  → {token, user, status}
    GET  /auth/me                                   → user
    POST /auth/logout                               → {ok}

Dev ergonomics: with DEBUG=true the generated OTP is returned in the /otp
response (and logged) so the demo works without a mail provider.
"""

import logging
import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.config import settings
from ..core.db import get_db
from ..core.security import create_token, generate_otp, get_current_user, hash_otp
from ..schemas import OtpIn, RegisterIn, VerifyIn
from ..services.serializers import aware, now, user_payload

log = logging.getLogger("root404.auth")
router = APIRouter()

MONTHS_FR = [
    "Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin",
    "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc.",
]


def _normalize(email: str) -> str:
    return email.strip().lower()


def _find_user(db: Session, email: str) -> models.User | None:
    q = select(models.User).where(models.User.email == email)
    return db.execute(q).scalar_one_or_none()


def _unique_username(db: Session, base: str) -> str:
    base = re.sub(r"[^a-z0-9_.-]", "", base.lower())[:20] or "student"
    candidate, i = base, 1
    q = select(models.User).where(models.User.username == candidate)
    while db.execute(q).scalar_one_or_none() is not None:
        i += 1
        candidate = f"{base}{i}"
    return candidate


def _default_avatar(username: str) -> str:
    # Deterministic pravatar pick per username
    img = (sum(ord(ch) for ch in username) % 68) + 1
    return f"https://i.pravatar.cc/160?img={img}"


def create_student(
    db: Session,
    *,
    email: str,
    full_name: str = "",
    display_name: str = "",
    campus: str = "Tunis",
    title: str = "Coder — Cursus C",
    status: str = "student",
) -> models.User:
    """Create a fresh student account (used by register + first OTP login)."""
    local = email.split("@")[0]
    username = _unique_username(db, local)
    display = display_name or re.sub(r"[._-]", " ", local).strip().title() or "Étudiant"
    full = full_name or display
    coalitions = db.execute(select(models.Coalition).order_by(models.Coalition.points.desc())).scalars().all()
    d = datetime.now(timezone.utc)
    user = models.User(
        username=username,
        email=email,
        display_name=display,
        full_name=full,
        title=title,
        campus=campus,
        avatar=_default_avatar(username),
        bio="",
        github=username,
        discord=f"{username}#404",
        site=f"root404.tn/u/{username}",
        status=status,
        joined=f"{MONTHS_FR[d.month - 1]} {d.year}",
        coalition_id=coalitions[0].id if coalitions else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/otp")
def request_otp(body: OtpIn, db: Session = Depends(get_db)):
    email = _normalize(body.email)

    # Resend rate limit
    q = (
        select(models.OtpCode)
        .where(models.OtpCode.email == email)
        .order_by(models.OtpCode.created_at.desc())
        .limit(1)
    )
    latest = db.execute(q).scalar_one_or_none()
    if latest is not None:
        if (now() - aware(latest.created_at)) < timedelta(seconds=settings.otp_resend_seconds):
            raise HTTPException(status_code=429, detail="Un code vient d'être envoyé — patiente 60 s.")

    code = generate_otp()
    db.add(models.OtpCode(
        email=email,
        code_hash=hash_otp(code),
        expires_at=now() + timedelta(minutes=settings.otp_ttl_minutes),
    ))
    db.commit()

    # In a real deployment this is where the e-mail would go out.
    log.info("OTP for %s: %s%s", email, code, "" if settings.debug else " (dev code hidden)")

    response = {"sent": True, "email": email}
    if settings.debug:
        response["dev_code"] = code
    return response


@router.post("/verify")
def verify_otp(body: VerifyIn, db: Session = Depends(get_db)):
    email = _normalize(body.email)
    code = body.code.strip()

    q = (
        select(models.OtpCode)
        .where(
            models.OtpCode.email == email,
            models.OtpCode.consumed.is_(False),
        )
        .order_by(models.OtpCode.created_at.desc())
        .limit(1)
    )
    otp = db.execute(q).scalar_one_or_none()

    if otp is None or aware(otp.expires_at) < now():
        raise HTTPException(status_code=400, detail="Code expiré — demande un nouveau code.")
    if otp.code_hash != hash_otp(code):
        raise HTTPException(status_code=401, detail="Code incorrect.")

    otp.consumed = True
    db.flush()

    user = _find_user(db, email)
    if user is None:
        # First connection with an unknown e-mail → open a student account
        # (42-style: the Piscine pipeline picks it up from here).
        user = create_student(db, email=email)

    db.commit()
    return {"token": create_token(user.id), "user": user_payload(user, db)}


@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    """Piscine application → pending student account."""
    email = _normalize(body.email)
    if _find_user(db, email) is not None:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet e-mail.")
    user = create_student(
        db,
        email=email,
        full_name=body.full_name.strip(),
        campus=body.campus,
        title="Candidat Piscine",
        status="piscine",
    )
    return {"token": create_token(user.id), "user": user_payload(user, db), "status": "piscine"}


@router.get("/me")
def me(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_payload(user, db)


@router.post("/logout")
def logout(user: models.User = Depends(get_current_user)):
    # Stateless JWT — the client drops its token. Kept for contract symmetry.
    return {"ok": True}
