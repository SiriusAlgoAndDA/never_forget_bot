import time

import jwt
import loguru

from bot import config
from bot.utils import external_request


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
