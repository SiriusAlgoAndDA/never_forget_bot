"""Add user

Revision ID: 12bea55a5eea
Revises:
Create Date: 2024-12-16 15:33:00.788751

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '12bea55a5eea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('tg_id', sa.String(), nullable=False),
        sa.Column('tg_username', sa.String(), nullable=True),
        sa.Column('tg_name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__user')),
        sa.UniqueConstraint('id', name=op.f('uq__user__id')),
    )
    op.create_index(op.f('ix__user__tg_id'), 'user', ['tg_id'], unique=True)
    op.create_index(op.f('ix__user__tg_username'), 'user', ['tg_username'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix__user__tg_username'), table_name='user')
    op.drop_index(op.f('ix__user__tg_id'), table_name='user')
    op.drop_table('user')
