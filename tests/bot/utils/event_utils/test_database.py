import datetime
import uuid

from bot.database import models
from bot.schemas.event import event_schemas
from bot.schemas.notification import notification_schemas
from bot.utils.event_utils import EventSortType, get_events_by_user_sorted, get_upcoming_notifications_by_user
from tests.factory_lib import event, user


async def test_get_events_by_user_sorted_empty(session):
    """Тест для случая, когда у пользователя нет событий."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    events = await get_events_by_user_sorted(session, user_obj.id, EventSortType.BY_EVENT_TIME)
    assert len(events) == 0


async def test_get_events_by_user_sorted_with_different_sorting(session, create_test_events_with_notifications):
    """Тест проверяет разную сортировку событий."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    event1, event2, _, _ = await create_test_events_with_notifications(session, user_obj)

    # Сортировка по времени события
    events_by_event_time = await get_events_by_user_sorted(session, user_obj.id, EventSortType.BY_EVENT_TIME)
    assert len(events_by_event_time) == 2
    assert events_by_event_time[0].id == event1.id  # Событие 1 раньше по времени
    assert events_by_event_time[1].id == event2.id  # Событие 2 позже по времени

    # Сортировка по времени уведомления
    events_by_notification_time = await get_events_by_user_sorted(
        session, user_obj.id, EventSortType.BY_NOTIFICATION_TIME
    )
    assert len(events_by_notification_time) == 2
    assert events_by_notification_time[0].id == event2.id  # Событие 2 имеет раннее уведомление
    assert events_by_notification_time[1].id == event1.id  # Событие 1 имеет позднее уведомление


async def test_get_upcoming_notifications_by_user_empty(session):
    """Тест для случая, когда у пользователя нет уведомлений."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    events = await get_upcoming_notifications_by_user(session, user_obj.id)
    assert len(events) == 0


async def test_get_upcoming_notifications_by_user_with_notifications(session, create_test_events_with_notifications):
    """Тест проверяет корректную сортировку по времени уведомления."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    event1, event2, _, _ = await create_test_events_with_notifications(session, user_obj)

    events = await get_upcoming_notifications_by_user(session, user_obj.id)
    assert len(events) == 2

    # Первым должно быть событие 2 (уведомление раньше)
    assert events[0].id == event2.id
    # Вторым должно быть событие 1 (уведомление позже)
    assert events[1].id == event1.id


async def test_get_upcoming_notifications_by_user_filters_completed_events(session):
    """Тест проверяет, что завершенные события не включаются в результат."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    now = datetime.datetime.now(datetime.timezone.utc)

    # Создаем завершенное событие
    completed_event = event.EventFactory(
        user_id=user_obj.id,
        name='Завершенное событие',
        time=now + datetime.timedelta(hours=1),
        status=event_schemas.EventStatus.COMPLETED,
    )

    session.add(completed_event)
    await session.commit()

    events = await get_upcoming_notifications_by_user(session, user_obj.id)
    assert len(events) == 0


async def test_get_upcoming_notifications_by_user_filters_sent_notifications(session):
    """Тест проверяет, что отправленные уведомления не включаются в результат."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    # Создаем событие
    event_obj = event.EventFactory(
        user_id=user_obj.id,
        name='Тестовое событие',
        time=now + datetime.timedelta(hours=1),
        status=event_schemas.EventStatus.PENDING,
    )

    session.add(event_obj)
    await session.commit()

    sent_notification = models.Notification(
        event_id=event_obj.id,
        notify_ts=now + datetime.timedelta(minutes=30),
        status=notification_schemas.NotificationStatus.SENT,
        workflow_id=f'workflow-{uuid.uuid4()}',
    )

    session.add(sent_notification)
    await session.commit()

    events = await get_upcoming_notifications_by_user(session, user_obj.id)
    assert len(events) == 0
