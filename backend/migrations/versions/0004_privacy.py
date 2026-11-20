"""Private-by-default portfolios, public directory opt-out, global session epoch."""
from alembic import op
import sqlalchemy as sa
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('public_profile', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('users', sa.Column('directory_visible', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('users', sa.Column('session_version', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('users', 'session_version')
    op.drop_column('users', 'directory_visible')
    op.drop_column('users', 'public_profile')
