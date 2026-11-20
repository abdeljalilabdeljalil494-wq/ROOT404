"""Explicit operator-scheduled retention, never an unannounced startup data purge."""
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.mentor import MentorInteraction
from app.models.submission import Submission
from app.models.room import RoomMessage
from app.models import AuditLog
from app.models.notification import Notification


def purge_expired(db, apply=False):
    result = {}
    for model, days in [(MentorInteraction, settings.MENTOR_RETENTION_DAYS),
                        (Submission, settings.SUBMISSION_RETENTION_DAYS),
                        (RoomMessage, settings.MESSAGE_RETENTION_DAYS),
                        (Notification, settings.NOTIFICATION_RETENTION_DAYS),
                        (AuditLog, settings.AUDIT_RETENTION_DAYS)]:
        if not 1 <= days <= 3650:
            raise ValueError('Retention days must be 1–3650')
        query = db.query(model).filter(model.created_at < datetime.utcnow() - timedelta(days=days))
        result[model.__tablename__] = query.count()
        if apply:
            query.delete(synchronize_session=False)
    if apply:
        db.commit()
    return result
