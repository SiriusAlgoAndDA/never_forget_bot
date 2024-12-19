"""add user's timezone

Revision ID: b88b6c6f4ed6
Revises: cdb60bbf90d4
Create Date: 2024-12-19 10:27:07.186912

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b88b6c6f4ed6'
down_revision = 'cdb60bbf90d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(op.f('uq__event__id'), 'event', ['id'])
    op.add_column('user', sa.Column('timezone', sa.Float(), server_default='3', nullable=False))


def downgrade() -> None:
    op.drop_column('user', 'timezone')
    op.drop_constraint(op.f('uq__event__id'), 'event', type_='unique')
