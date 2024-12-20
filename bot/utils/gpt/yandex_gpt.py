import loguru

from bot import config
from bot.database import models
from bot.utils import external_request, user_utils
from bot.utils.common import yandex_utils


async def request_to_gpt(text: str, user: models.User, iam_token: str | None = None) -> str:
    user_time = await user_utils.current_time(user)
    with open('promt.txt', 'r', encoding='utf-8') as f:
        text_promt = f.read()
    promt = {
        'modelUri': f'gpt://{config.get_settings().YANDEX_CLOUD_CATALOG_ID}/yandexgpt/latest',
        'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': '2000'},
        'messages': [
            {
                'role': 'system',
                'text': text_promt.format(cur_time=user_time),
            },
            {'role': 'user', 'text': text},
        ],
    }

    token = iam_token or await yandex_utils.get_iam_token()
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
