import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models


class NotificationStatus(StrEnum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


async def get_notification(session: AsyncSession, notification_id: uuid.UUID) -> models.Notification | None:
    """
    Получить событие (Notification) по его ID.

    :param session: SQLAlchemy Async сессия.
    :param notification_id: UUID события.
    :return: Объект Notification, если найден, или None.
    """
    query = select(models.Notification).where(models.Notification.id == notification_id)
    return await session.scalar(query)


async def update_notification_status(
    session: AsyncSession, notification_id: uuid.UUID, new_status: str
) -> models.Notification | None:
    """
    Обновить статус уведомления (Notification) по ID.

    :param session: SQLAlchemy Async сессия.
    :param notification_id: UUID уведомления.
    :param new_status: Новый статус уведомления.
    :return: Обновлённый объект Notification, если найден, или None.
    """
    notification = await get_notification(session, notification_id)
    if not notification:
        return None

    notification.status = new_status
    await session.flush()
    await session.refresh(notification)
    return notification


async def add_notification(
    session: AsyncSession,
    event_id: uuid.UUID,
    notify_ts: datetime,
    workflow_id: str,
    status: str = 'pending',
    sent_ts: datetime | None = None,
) -> models.Notification:
    """
    Добавить новое уведомление (Notification) в базу данных.

    :param session: SQLAlchemy Async сессия.
    :param event_id: UUID связанного события.
    :param notify_ts: Время уведомления (notify timestamp).
    :param workflow_id: Идентификатор связанного workflow.
    :param status: Статус уведомления (по умолчанию PENDING).
    :param sent_ts: Время отправки (опционально).
    :return: Созданный объект Notification.
    """
    new_notification = models.Notification(
        id=uuid.uuid4(),
        event_id=event_id,
        notify_ts=notify_ts,
        workflow_id=workflow_id,
        status=status,
        sent_ts=sent_ts,
    )

    session.add(new_notification)
    await session.flush()
    await session.refresh(new_notification)
    return new_notification


async def update_sent_ts(
    session: AsyncSession, notification_id: uuid.UUID, new_sent_ts: datetime
) -> models.Notification | None:
    """
    Обновить статус уведомления (Notification) по ID.

    :param session: SQLAlchemy Async сессия.
    :param notification_id: UUID уведомления.
    :param new_status: Новый статус уведомления.
    :return: Обновлённый объект Notification, если найден, или None.
    """
    notification = await get_notification(session, notification_id)
    if not notification:
        return None

    notification.sent_ts = new_sent_ts
    await session.flush()
    await session.refresh(notification)
    return notification
