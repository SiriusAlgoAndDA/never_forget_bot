# pylint: disable=unsubscriptable-object  # TODO
import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel
from .user import User


class Event(BaseModel):
    __tablename__ = 'event'

    type: orm.Mapped[str] = sa.Column(
        'type',
        sa.String,
        nullable=False,
        index=True,
    )

    name: orm.Mapped[str] = sa.Column('name', sa.String, nullable=False, index=False, doc='Само событие')

    status: orm.Mapped[str] = sa.Column(
        'status', sa.String, nullable=False, default='pending', index=True, doc='Статус события: pending, completed...'
    )

    time: orm.Mapped[datetime.datetime] = sa.Column(
        'time', sa.TIMESTAMP(timezone=True), nullable=False, doc='Время события datetime'
    )

    reschedule_timedelta: orm.Mapped[datetime.timedelta] = sa.Column(
        'reschedule_timedelta',
        sa.Interval,
        default=datetime.timedelta(minutes=10),
        nullable=True,
        doc='Интервал для пересчёта (timedelta)',
    )

    user_id: orm.Mapped[uuid.UUID | str] = sa.Column(  # type: ignore
        sa.ForeignKey('user.id'),
        nullable=False,
        index=True,
        doc='Идентификатор пользователя (UUID)',
    )
    user: orm.Mapped[User] = orm.relationship(  # type: ignore
        User,
        foreign_keys=[user_id],
        doc='User',
    )
