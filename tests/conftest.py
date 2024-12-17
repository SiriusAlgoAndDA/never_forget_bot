# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=too-many-lines
import pathlib
import tempfile
import typing as tp
from os import environ
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy_utils import create_database, database_exists, drop_database

from bot import config
from bot.database.connection import SessionManager
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
    return make_alembic_config(cmd_options)


@pytest.fixture
def migrated_postgres(alembic_config: Config):
    """
    Проводит миграции.
    """
    upgrade(alembic_config, 'head')


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
    with open(tmp_filename, 'w', encoding='utf-8') as f:
        f.write('test')
    yield tmp_filename
    pathlib.Path(tmp_filename).unlink()
