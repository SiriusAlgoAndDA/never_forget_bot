from typing import BinaryIO

import loguru

from bot import config
from bot.utils.common import yandex_utils
from bot.utils.external_request.service import make_request


async def speech_request(file: BinaryIO) -> str:
    catalog_id = config.get_settings().YANDEX_CLOUD_CATALOG_ID
    token = await yandex_utils.get_iam_token()
    params = '&'.join(['topic=general', f'folderId={catalog_id}', 'lang=ru-RU'])
    response = await make_request(
        url=f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}',
        logger=loguru.logger,
        method='POST',
        data=file,
        custom_headers={'Authorization': f'Bearer {token}'},
    )
    decoded_data = response.json()['result']
    if decoded_data.get('error_code') is None:
        return decoded_data.get('result')
    else:
        raise RuntimeError()
