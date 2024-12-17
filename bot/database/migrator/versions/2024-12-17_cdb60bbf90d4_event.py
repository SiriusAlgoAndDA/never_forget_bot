"""Add event table

Revision ID: cdb60bbf90d4
Revises: 12bea55a5eea
Create Date: 2024-12-17 12:55:19.296507

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'cdb60bbf90d4'
down_revision = '12bea55a5eea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'event',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column(
            'dt_created',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk__event__user_id__user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__event')),
        sa.UniqueConstraint('id', name=op.f('uq__event__id')),
    )
    op.create_index(op.f('ix__event__type'), 'event', ['type'], unique=False)
    op.create_index(op.f('ix__event__user_id'), 'event', ['user_id'], unique=False)
    op.create_unique_constraint(op.f('uq__user__id'), 'user', ['id'])


def downgrade() -> None:
    op.drop_constraint(op.f('uq__user__id'), 'user', type_='unique')
    op.drop_index(op.f('ix__event__user_id'), table_name='event')
    op.drop_index(op.f('ix__event__type'), table_name='event')
    op.drop_table('event')
