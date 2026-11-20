"""Durable mission reward claims and private room moderation."""
from alembic import op
import sqlalchemy as sa
revision='0007'
down_revision='0006'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('room_messages',sa.Column('removed_at',sa.DateTime(),nullable=True))
    op.create_table('mission_claims',
        sa.Column('id',sa.String(32),primary_key=True),
        sa.Column('user_id',sa.String(32),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('day',sa.String(10),nullable=False),
        sa.Column('submission_id',sa.String(32),sa.ForeignKey('submissions.id',ondelete='SET NULL')),
        sa.Column('xp',sa.Integer(),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False),
        sa.UniqueConstraint('user_id','day'))
    op.create_index('ix_mission_claims_user_id','mission_claims',['user_id'])
    op.create_table('moderation_reports',
        sa.Column('id',sa.String(32),primary_key=True),
        sa.Column('user_id',sa.String(32),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('message_id',sa.String(32),sa.ForeignKey('room_messages.id',ondelete='CASCADE'),nullable=False),
        sa.Column('reason',sa.String(1000),nullable=False),sa.Column('status',sa.String(16),nullable=False),
        sa.Column('reviewer_id',sa.String(32),sa.ForeignKey('users.id',ondelete='SET NULL')),
        sa.Column('created_at',sa.DateTime(),nullable=False),sa.Column('resolved_at',sa.DateTime()),
        sa.UniqueConstraint('user_id','message_id'))
    op.create_index('ix_moderation_reports_user_id','moderation_reports',['user_id'])
    op.create_index('ix_moderation_reports_status','moderation_reports',['status'])


def downgrade():
    op.drop_table('moderation_reports');op.drop_table('mission_claims')
    op.drop_column('room_messages','removed_at')
