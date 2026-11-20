"""Private, transactionally-created in-app notifications (not email delivery)."""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from app.core.database import Base


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = (Index('ix_notifications_owner_created', 'user_id', 'created_at', 'id'),)
    id = Column(String(32), primary_key=True, default=lambda: 'n_' + uuid.uuid4().hex[:28])
    user_id = Column(String(32), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    kind = Column(String(50), nullable=False)
    text = Column(String(500), nullable=False)
    path = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {'id': self.id, 'kind': self.kind, 'text': self.text, 'path': self.path,
                'created_at': self.created_at.isoformat() + 'Z',
                'read_at': self.read_at.isoformat() + 'Z' if self.read_at else None}
