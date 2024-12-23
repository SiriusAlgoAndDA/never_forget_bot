import typing
import uuid
from datetime import datetime

import sqlalchemy
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models
from bot.schemas.event import event_schemas
from bot.schemas.notification import notification_schemas


async def get_notification(session: AsyncSession, notification_id: uuid.UUID | str) -> models.Notification | None:
    """
    Получить событие (Notification) по его ID.

    :param session: SQLAlchemy Async сессия.
    :param notification_id: UUID события.
    :return: Объект Notification, если найден, или None.
    """
    query = select(models.Notification).where(models.Notification.id == notification_id)
    return await session.scalar(query)


async def update_notification_status(session: AsyncSession, notification_id: uuid.UUID | str, new_status: str) -> None:
    """
    Обновить статус уведомления (Notification) по ID.

    :param session: SQLAlchemy Async сессия.
    :param notification_id: UUID уведомления.
    :param new_status: Новый статус уведомления.
    :return: None.
    """
    query = update(models.Notification).where(models.Notification.id == notification_id).values(status=new_status)
    await session.execute(query)


async def add_notification(  # pylint: disable=too-many-arguments
    session: AsyncSession,
    event_id: uuid.UUID | str,
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


async def update_sent_ts(session: AsyncSession, notification_id: uuid.UUID | str, new_sent_ts: datetime) -> None:
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
    query = update(models.Notification).where(models.Notification.id == notification_id).values(sent_ts=new_sent_ts)
    await session.execute(query)


async def get_active_notification_by_event_id(
    session: AsyncSession, event_id: uuid.UUID | str
) -> typing.Sequence[models.Notification]:
    """
    Получить все активные события (Notification) по ID события.

    :param session: SQLAlchemy Async сессия.
    :param event_id: UUID события.
    :return: Список с Notification, если найден, или [].
    """
    query = (
        select(models.Notification)
        .where(models.Notification.event_id == event_id)
        .where(models.Notification.status == notification_schemas.NotificationStatus.PENDING)
    )
    return (await session.execute(query)).scalars().all()


async def get_active_notifications_by_user(
    session: AsyncSession, user_id: str | uuid.UUID
) -> typing.Sequence[sqlalchemy.Row[tuple[uuid.UUID | str, str, datetime, datetime]]]:
    """
    Получить список активных событий (Event) и нотификаций.

    :param session: SQLAlchemy Async сессия
    :param user_id: ID пользователя.
    :return: Tuple с именем события, временем события и временем уведомления.
    """
    query = (
        select(
            models.Event.id,
            models.Event.name,
            models.Event.time,
            func.min(models.Notification.notify_ts).label('next_notify_ts'),
        )
        .where(models.Notification.event_id == models.Event.id)
        .where(models.Event.user_id == models.User.id)
        .where(models.User.id == user_id)
        .where(models.Notification.status == notification_schemas.NotificationStatus.PENDING)
        .where(models.Event.status == event_schemas.EventStatus.PENDING)
        .group_by(models.Event.id)
    )
    return (await session.execute(query)).fetchall()
