import typing
import uuid
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models
from bot.schemas.event import event_schemas
from bot.schemas.notification import notification_schemas


async def get_event(session: AsyncSession, event_id: uuid.UUID | str) -> models.Event | None:
    """
    Получить событие (Event) по его ID.

    :param session: SQLAlchemy Async сессия.
    :param event_id: UUID события.
    :return: Объект Event, если найден, или None.
    """
    query = select(models.Event).where(models.Event.id == event_id)
    return await session.scalar(query)


async def add_event(  # pylint: disable=too-many-arguments
    session: AsyncSession,
    event_type: str,
    name: str,
    time: datetime,
    user_id: uuid.UUID | str,
    status: str = event_schemas.EventStatus.PENDING,
    reschedule_timedelta: timedelta = timedelta(minutes=10),
) -> models.Event:
    """
    Добавить новое событие (Event) в базу данных.

    :param session: SQLAlchemy Async сессия.
    :param event_type: Тип события.
    :param name: Имя события.
    :param status: Статус события, по умолчанию 'pending'.
    :param time: Время события (datetime), обязательно.
    :param reschedule_timedelta: Интервал для пересчёта, опционально.
    :param user_id: UUID пользователя, обязательно.
    :return: Созданный объект Event.
    """

    new_event = models.Event(
        type=event_type,
        name=name,
        status=status,
        time=time,
        reschedule_timedelta=reschedule_timedelta,
        user_id=user_id,
    )

    session.add(new_event)
    await session.flush()
    await session.refresh(new_event)
    return new_event


async def update_event_status(
    session: AsyncSession, event_id: uuid.UUID | str, new_status: event_schemas.EventStatus | str
) -> models.Event | None:
    """
    Обновить статус события (Event) по его ID.

    :param session: SQLAlchemy Async сессия.
    :param event_id: UUID события.
    :param new_status: Новый статус события.
    :return: Обновлённый объект Event, если найден, или None.
    """
    query = select(models.Event).where(models.Event.id == event_id)
    event = await session.scalar(query)

    if not event:
        return None

    event.status = new_status

    await session.flush()
    await session.refresh(event)
    return event


async def get_active_events_by_user(
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
        .order_by(models.Event.time)
    )
    return (await session.execute(query)).fetchall()
