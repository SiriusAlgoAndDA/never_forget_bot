import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel


class Event(BaseModel):
    __tablename__ = 'event'

    name: orm.Mapped[str] = sa.Column(
        'name',
        sa.String,
        nullable=False,
        index=False,
        doc = "Само событие"
    )

    status: orm.Mapped[str] = sa.Column(
        'status',
        sa.String,
        nullable=False,
        default='pending',
        index=True,
        doc = "Статус события: pending, completed..."
    )

    time: orm.Mapped[datetime.datetime] = sa.Column(
        'time',
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        doc = "Время события datetime"
    )

    reschedule_timedelta: orm.Mapped[datetime.timedelta] = sa.Column(
        'reschedule_timedelta',
        sa.Interval,
        nullable=True,
        doc = "Интервал для пересчёта (timedelta)"
    )

    user_id: orm.Mapped[uuid.UUID] = sa.Column(  # type: ignore
        'user_id',  
        sa.UUID(as_uuid=True),
        sa.ForeignKey('user.id'),
        nullable=False,
        index=True,
        doc = "Идентификатор пользователя (UUID)"
    )
