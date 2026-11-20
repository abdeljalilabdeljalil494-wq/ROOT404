"""Persist provider-backed mentor interactions, no seeded or synthetic history."""
from alembic import op
import sqlalchemy as sa
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('mentor_interactions',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_mentor_user_created', 'mentor_interactions', ['user_id', 'created_at'])


def downgrade():
    op.drop_index('ix_mentor_user_created', table_name='mentor_interactions')
    op.drop_table('mentor_interactions')
