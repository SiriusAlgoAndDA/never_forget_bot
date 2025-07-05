# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=too-many-lines
import datetime
import pathlib
import tempfile
import typing as tp
import uuid
from os import environ
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from aiogram.types import Message
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists, drop_database

from bot import config
from bot.database import models
from bot.database.connection import SessionManager
from bot.schemas.event import event_schemas
from bot.schemas.notification import notification_schemas
from tests.factory_lib import event
from tests.utils import make_alembic_config


@pytest.fixture
async def postgres() -> str:  # type: ignore
    """
    Создает временную БД для запуска теста.
    """
    settings = config.get_settings()

    tmp_name = '.'.join([uuid4().hex, 'pytest'])
    settings.POSTGRES_DB = tmp_name
    environ['POSTGRES_DB'] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    await SessionManager().refresh()

    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)


@pytest.fixture
def alembic_config(postgres) -> Config:
    """
    Создает файл конфигурации для alembic.
    """
    cmd_options = SimpleNamespace(
        config='',
        name='alembic',
        pg_url=postgres,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_opts=cmd_options)


@pytest.fixture
def migrated_postgres(alembic_config: Config):
    """
    Проводит миграции.
    """
    upgrade(config=alembic_config, revision='head')


@pytest.fixture
async def create_async_session(  # type: ignore
    migrated_postgres, manager: SessionManager = SessionManager()
) -> tp.Callable:  # type: ignore
    """
    Returns a class object with which you can
    create a new session to connect to the database.
    """
    await manager.refresh()  # Very important! Use this in `client` function.
    yield manager.create_async_session


@pytest.fixture
async def session(create_async_session):  # type: ignore
    """
    Creates a new session to connect to the database.
    """
    async with create_async_session() as session:
        yield session


@pytest.fixture
def tmp_file():
    tmp_filename = tempfile.mktemp()
    with open(file=tmp_filename, mode='w', encoding='utf-8') as f:
        f.write('test')
    yield tmp_filename
    pathlib.Path(tmp_filename).unlink()


@pytest.fixture
def message():
    """Мок объект для Telegram Message."""
    message = Mock(spec=Message)
    message.reply = AsyncMock()
    return message


@pytest.fixture
def state():
    """Мок объект для aiogram FSM state."""
    state = AsyncMock()
    state.clear = AsyncMock()
    return state


@pytest.fixture
async def create_test_events_with_notifications():
    """Создание тестовых событий и уведомлений для использования в тестах.

    Создает два события:
    - Событие 1: время события раньше, но уведомление позже
    - Событие 2: время события позже, но уведомление раньше

    Возвращает: функцию, которая принимает (session, user_obj)
        и возвращает (event1, event2, notification1, notification2)
    """

    async def _create_test_events_with_notifications(session, user_obj):
        # Создаем события
        now = datetime.datetime.now(datetime.timezone.utc)

        # Событие 1: время события раньше, но уведомление позже
        event1 = event.EventFactory(
            user_id=user_obj.id,
            name='Событие 1',
            time=now + datetime.timedelta(hours=1),
            status=event_schemas.EventStatus.PENDING,
        )

        # Событие 2: время события позже, но уведомление раньше
        event2 = event.EventFactory(
            user_id=user_obj.id,
            name='Событие 2',
            time=now + datetime.timedelta(hours=2),
            status=event_schemas.EventStatus.PENDING,
        )

        session.add_all([event1, event2])
        await session.commit()

        # Создаем уведомления
        notification1 = models.Notification(
            event_id=event1.id,
            notify_ts=now + datetime.timedelta(minutes=90),  # позже по времени
            status=notification_schemas.NotificationStatus.PENDING,
            workflow_id=f'workflow-{uuid.uuid4()}',
        )

        notification2 = models.Notification(
            event_id=event2.id,
            notify_ts=now + datetime.timedelta(minutes=30),  # раньше по времени
            status=notification_schemas.NotificationStatus.PENDING,
            workflow_id=f'workflow-{uuid.uuid4()}',
        )

        session.add_all([notification1, notification2])
        await session.commit()

        return event1, event2, notification1, notification2

    return _create_test_events_with_notifications
