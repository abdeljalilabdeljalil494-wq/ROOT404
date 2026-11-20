"""One-use browser-bound OAuth attempts and explicit external identities."""
from alembic import op
import sqlalchemy as sa
revision='0006'
down_revision='0005'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('oauth_identities',
        sa.Column('id',sa.String(32),primary_key=True),
        sa.Column('user_id',sa.String(32),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('provider',sa.String(16),nullable=False),sa.Column('subject',sa.String(255),nullable=False),
        sa.Column('created_at',sa.DateTime(),nullable=False),
        sa.UniqueConstraint('provider','subject'),sa.UniqueConstraint('user_id','provider'))
    op.create_index('ix_oauth_identities_user_id','oauth_identities',['user_id'])
    op.create_table('oauth_attempts',
        sa.Column('state_hash',sa.String(64),primary_key=True),sa.Column('browser_hash',sa.String(64),nullable=False),
        sa.Column('provider',sa.String(16),nullable=False),sa.Column('verifier',sa.String(128),nullable=False),
        sa.Column('nonce',sa.String(128),nullable=False),
        sa.Column('user_id',sa.String(32),sa.ForeignKey('users.id',ondelete='CASCADE')),
        sa.Column('session_version',sa.Integer()),sa.Column('expires_at',sa.DateTime(),nullable=False))
    op.create_index('ix_oauth_attempts_expires_at','oauth_attempts',['expires_at'])


def downgrade():
    op.drop_table('oauth_attempts'); op.drop_table('oauth_identities')
