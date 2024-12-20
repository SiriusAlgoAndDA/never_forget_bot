import uuid
from datetime import datetime, timedelta
from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models


async def get_event(session: AsyncSession, event_id: uuid.UUID) -> models.Event | None:
    """
    Получить событие (Event) по его ID.

    :param session: SQLAlchemy Async сессия.
    :param event_id: UUID события.
    :return: Объект Event, если найден, или None.
    """
    query = select(models.User).where(models.Event.id == event_id)
    return await session.scalar(query)


async def add_event(
    session: AsyncSession,
    event_type: str,
    name: str,
    time: datetime,
    user_id: uuid.UUID,
    status: str = 'pending',
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


class EventStatus(StrEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    DELETED = 'deleted'
    NOT_COMPLETED = 'not_completed'


async def update_event_status(session: AsyncSession, event_id: uuid.UUID, new_status: str) -> models.Event | None:
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
