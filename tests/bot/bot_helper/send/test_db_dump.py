import pathlib

import pytest

from bot.bot_helper import send
from bot.config import get_settings


pytestmark = pytest.mark.asyncio


class TestSendDbDumpHandler:
    async def test_send_db_dump(self, tmp_file, mock_bot):
        settings = get_settings()
        await send.send_db_dump(tmp_file)
        mock_bot.send_document.assert_called_once()
        assert pathlib.Path(mock_bot.send_document.call_args[1]['document'].path) == pathlib.Path(tmp_file)
        assert mock_bot.send_document.call_args[1]['chat_id'] == settings.TG_DB_DUMP_CHAT_ID
        assert mock_bot.send_document.call_args[1]['caption'] == settings.PROJECT_NAME
        assert mock_bot.send_document.call_args[1]['disable_notification'] is True
