import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from .base import BaseModel


class Notification(BaseModel):
    __tablename__ = 'notification'
    
    event_id: orm.Mapped[uuid.UUID] = sa.Column(  # type: ignore
        'event_id',
        sa.UUID(as_uuid=True),
        sa.ForeignKey('event.id'),
        nullable=False,
        index=True,
        doc="ID event'а",
    )

    notify_ts: orm.Mapped[datetime.datetime] = sa.Column(
        'notify_ts', sa.TIMESTAMP(timezone=True), nullable=False, doc='Время напоминания'
    )

    sent_ts: orm.Mapped[datetime.datetime | None] = sa.Column(
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
