import time

import jwt
import loguru
from aiogram.types import Message

from bot import config
from bot.database import models
from bot.utils import external_request, user_utils


async def get_iam_token() -> str:
    settings = config.get_settings()
    key_id = settings.YANDEX_CLOUD_KEY_ID
    service_account_id = settings.YANDEX_CLOUD_SERVICE_ACCOUNT_ID
    with open(settings.YANDEX_CLOUD_PRIVATE_KEY_FILE, 'r', encoding='utf-8') as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600,
    }

    # Формирование JWT
    encoded_token = jwt.encode(payload, private_key, algorithm='PS256', headers={'kid': key_id})

    response = await external_request.make_request(
        url='https://iam.api.cloud.yandex.net/iam/v1/tokens',
        logger=loguru.logger,
        method='POST',
        data={'jwt': encoded_token},
        content_type='application/json',
    )
    if response.status_code != 200:
        raise RuntimeError(f'Got {response.status_code} status code: {response.text}')

    return response.json()['iamToken']


async def request_to_gpt(message: Message, user: models.User) -> str:
    user_time = await user_utils.current_time(user)
    with open('promt.txt', 'r') as f:
        text_promt = f.read()
    promt = {
        'modelUri': f'gpt://{config.get_settings().YANDEX_CLOUD_CATALOG_ID}/yandexgpt/latest',
        'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': '2000'},
        'messages': [
            {
                'role': 'system',
                'text': text_promt.format(cur_time = user_time),
            },
            {'role': 'user', 'text': message.text},
        ],
    }
    token = await get_iam_token()
    response = await external_request.make_request(
        url='https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
        logger=loguru.logger,
        method='POST',
        data=promt,
        custom_headers={'Authorization': f'Bearer {token}'},
        content_type='application/json',
    )

    if response.status_code != 200:
        raise RuntimeError(f'Got {response.status_code} status code: {response.text}')

    data = response.json()['result']['alternatives'][0]['message']['text']
    data = data.strip('`').strip()
    return data
