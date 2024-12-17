import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel


class Event(BaseModel):
    __tablename__ = 'event'

    type: orm.Mapped[str] = sa.Column(
        'type',
        sa.String,
        nullable=False,
        index=True,
    )
    name: orm.Mapped[str] = sa.Column(
        'name',
        sa.String,
        nullable=False,
    )
    time: orm.Mapped[datetime.datetime] = sa.Column(
        'time',
        sa.TIMESTAMP(timezone=True),
        nullable=False,
    )

    user_id: orm.Mapped[uuid.UUID] = sa.Column(  # type: ignore
        'user_id',
        sa.UUID(as_uuid=True),
        sa.ForeignKey('user.id'),
        nullable=False,
        index=True,
    )
