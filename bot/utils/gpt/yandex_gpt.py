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
    promt = {
        'modelUri': f'gpt://{config.get_settings().YANDEX_CLOUD_CATALOG_ID}/yandexgpt',
        'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': '2000'},
        'messages': [
            {
                'role': 'system',
                'text': f"""Сейчас {user_time}. Мне нужен JSON с информацией о событии,
                которое мне нужно сохранить для напоминания в будущем.
                Готовый JSON должен иметь следующий формат:

    {{
      "event": <event_name, str>,
      "date_of_event": <<time_of_event, hh:mm:ss> <date_of_event, dd.mm.yyyy>>,
      "date_of_notify": <<time_of_notify, hh:mm:ss> <date_of_notify, dd.mm.yyyy>>,
      "type_of_event": <type, str>
    }}

    event – событие, о котором нужно напомнить,
    date_of_event – время и дата самого события, которое нужно выполнить
    date_of_notify – время и дата напоминания о событии
    type_of_event – тип события, один из 4:
    - моментальное (например, "принять лекарство", "полить цветы", тогда date_of_notify = date_of_event),
    - с подготовкой (например, "пойти в кино", "поезд", тогда date_of_notify = date_of_event - 20m),
    - регулярное моментальное (событие повторяется через равные промежутки времени и date_of_event == date_of_notify).
    - регулярное с подготовкой (событие повторяется через равные промежутки времени и date_of_event != date_of_notify).
    Если в описании события не указано конкретное время,
    нужно приблизительно определять его самостоятельно по контексту описываемого события.
    Также нужно учитывать, что бывают события, о которых нужно напоминать заранее,
    а бывают те, о которых можно напоминать аккурат в обозначенную дату начала события.
    Если тебе не удается определить какой-то из параметров,
    вставь в качестве значения соответствующей строки параметр Null.

    Пример №1: «Напомни мне принять таблетки завтра в 10 утра». В этом случае JSON будет выглядеть так:

    {{
      "event": "принять таблетки",
      "date_of_event": "10:00:00 19.12.2024",
      "date_of_notify": "10:00:00 19.12.2024",
      "type_of_event": "moment"
    }}

    Пример №2: "Напомни мне пойти в кино с друзьями завтра в 17:30":

    {{
      "event": "пойти в кино с друзьями",
      "date_of_event": "17:30:00 19.12.2024",
      "date_of_notify": "16:30:00 19.12.2024",
      "type_of_event": "prepar"
    }}
    """,
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
