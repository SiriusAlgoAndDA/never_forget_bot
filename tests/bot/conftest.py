# pylint: disable=unused-argument
import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram import types
from aiogram.exceptions import TelegramBadRequest


@pytest.fixture(name='bot')
async def bot_fixture():
    """Bot fixture"""
    _bot = Mock()
    _bot.send_document = AsyncMock()
    _bot.send_message = AsyncMock()

    def _side_effect(text, **kwargs):
        if len(text) == 4000 and '<code>' in text:
            raise TelegramBadRequest(
                method=None,  # type: ignore
                message="Can't parse entities: can't find end tag corresponding to start tag code",
            )
        return types.Message(
            message_id=46456,
            chat=types.Chat(id=1, type='type'),
            date=datetime.datetime.now(),
        )

    _bot.send_message.side_effect = _side_effect
    _bot.send_media_group = AsyncMock()
    _bot.pin_chat_message = AsyncMock()
    _bot.edit_message_text = AsyncMock()
    yield _bot


@pytest.fixture
async def mock_bot(mocker, bot):
    """Mock bot fixture"""
    mock = mocker.patch('bot.bot_helper.bot.bot', bot)
    return mock


@pytest.fixture
def mock_message_id(mocker):
    """Mock message id fixture"""
    mock = mocker.patch(
        'bot.bot_helper.send.ping_status.MESSAGE_ID',
        types.Message(
            message_id=46456,
            chat=types.Chat(id=1, type='type'),
            date=datetime.datetime.now(),
        ),
    )
    return mock
