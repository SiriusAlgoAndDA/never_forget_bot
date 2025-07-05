# pylint: disable=unsubscriptable-object  # TODO: SQLAlchemy 2.0 compatibility
import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel
from .event import Event


class Notification(BaseModel):
    __tablename__ = 'notification'

    event_id: orm.Mapped[uuid.UUID | str] = sa.Column(  # type: ignore
        sa.ForeignKey(Event.id),
        nullable=False,
        index=True,
        doc='Event id',
    )
    event: orm.Mapped[Event] = orm.relationship(  # type: ignore
        Event,
        foreign_keys=[event_id],
        doc='Event',
    )

    notify_ts: orm.Mapped[datetime.datetime] = sa.Column(
        'notify_ts', sa.TIMESTAMP(timezone=True), nullable=False, doc='Время напоминания'
    )

    sent_ts: orm.Mapped[datetime.datetime | None] = sa.Column(  # type: ignore[misc]
        'sent_ts', sa.TIMESTAMP(timezone=True), nullable=True, doc='Время последней отправки'
    )

    status: orm.Mapped[str] = sa.Column(
        'status',
        sa.String(),
        nullable=False,
        default='pending',
        index=True,
        doc='Статус отправки, pending, sent, terminated и т.д.',
    )

    # Идентификатор рабочего процесса
    workflow_id: orm.Mapped[str] = sa.Column(
        'workflow_id', sa.String, nullable=False, index=True, unique=True, doc='ID workflow в Temporal'
    )
