"""Owner-scoped notifications. Learners cannot create or send arbitrary alerts."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, rate_limit
from app.models.user import User
from app.models.notification import Notification

router = APIRouter(prefix='/notifications', tags=['Notifications'])


def notification_rate_limit(request: Request, user: User = Depends(get_current_user)):
    return rate_limit(request, max_requests=60, window=60, key_prefix='notifications:' + user.id)


@router.get('')
def list_notifications(response: Response, limit: int = Query(20, ge=1, le=100),
                       offset: int = Query(0, ge=0, le=10000),
                       user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    response.headers['Cache-Control'] = 'no-store'
    owned = Notification.user_id == user.id
    rows = db.scalars(select(Notification).where(owned).order_by(
        Notification.created_at.desc(), Notification.id.desc()).offset(offset).limit(limit)).all()
    unread = db.scalar(select(func.count()).select_from(Notification).where(owned, Notification.read_at.is_(None)))
    return {'items': [row.to_dict() for row in rows], 'unread_count': unread, 'offset': offset, 'limit': limit}


@router.post('/read-all', dependencies=[Depends(notification_rate_limit)])
def read_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.execute(update(Notification).where(Notification.user_id == user.id,
        Notification.read_at.is_(None)).values(read_at=datetime.utcnow()))
    db.commit()
    return {'ok': True, 'updated': result.rowcount}


@router.post('/{notification_id}/read', dependencies=[Depends(notification_rate_limit)])
def mark_read(notification_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if notification is None:
        raise HTTPException(404, 'Notification not found')
    if notification.read_at is None:
        notification.read_at = datetime.utcnow()
        db.commit()
    return notification.to_dict()
