import typing
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import aiogram
import loguru
import pytimeparse
from temporalio import activity, workflow

from bot import config
from bot.database.connection import SessionManager
from bot.markups import notify_markup
from bot.schemas.notify_workflow import notify_workflow_schemas
from bot.schemas.process_message_workflow import process_message_workflow_schemas
from bot.utils import event_utils, notification_utils, user_utils
from bot.utils.event_utils import add_event
from bot.utils.notification_utils import add_notification

from .notify_workflow import add_new_workflow


def validate_json(info: process_message_workflow_schemas.MessageInfo) -> dict[str, typing.Any] | None:
    """{{
        "event": <event_name, str>,
        "date_of_event": <<time_of_event, hh:mm:ss> <date_of_event, dd.mm.yyyy>>,
        "date_of_notify": <<time_of_notify, hh:mm:ss> <date_of_notify, dd.mm.yyyy>>,
        "type_of_event": <type, str>,
        "repeat_interval": <interval, str or null>
    }}"""
    if not info.gpt_json:
        loguru.logger.info('Got null gpt_json')
        return None
    data = deepcopy(info.gpt_json)
    try:
        if not isinstance(data['event'], str):
            loguru.logger.info('Type of "event" {} is not str', type(data['event']))
            return None
        date_of_event = datetime.strptime(data['date_of_event'], '%H:%M:%S %d.%m.%Y').replace(
            tzinfo=timezone(timedelta(hours=info.user_tz))
        )
        date_of_notify = datetime.strptime(data['date_of_notify'], '%H:%M:%S %d.%m.%Y').replace(
            tzinfo=timezone(timedelta(hours=info.user_tz))
        )

        if date_of_event < date_of_notify:
            loguru.logger.info('Date of event {} is before date of notify {}', date_of_event, date_of_notify)
            date_of_notify = date_of_event

        data['date_of_event'] = date_of_event.isoformat()
        data['date_of_notify'] = date_of_notify.isoformat()
        if not isinstance(data['type_of_event'], str):
            loguru.logger.info('Type of "type_of_event" {} is not str', type(data['type_of_event']))
            return None
        if data['repeat_interval'] is not None:
            data['repeat_interval'] = timedelta(seconds=pytimeparse.parse(data['repeat_interval']))
    except Exception as exc:  # pylint: disable=broad-exception-caught
        loguru.logger.exception('Failed to parse json: {}', exc)
        return None
    data['as_is'] = False
    return data


def AsIsJson(info: process_message_workflow_schemas.MessageInfo) -> dict[str, typing.Any]:
    data = {
        'event': info.message_text,
        'date_of_event': (datetime.now(timezone(timedelta(hours=info.user_tz))) + timedelta(hours=1)).isoformat(),
        'date_of_notify': (datetime.now(timezone(timedelta(hours=info.user_tz))) + timedelta(hours=1)).isoformat(),
        'type_of_event': 'moment',
        'repeat_interval': None,
        'as_is': True,
    }
    return data


@activity.defn
async def add_event_process(
    data: process_message_workflow_schemas.MessageInfoRequired,
) -> notify_workflow_schemas.NotifyData:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        date_of_event = datetime.fromisoformat(data.gpt_json['date_of_event'])
        date_of_notify = datetime.fromisoformat(data.gpt_json['date_of_notify'])
        event = await add_event(
            session,
            data.gpt_json['type_of_event'],
            data.gpt_json['event'],
            date_of_event,
            data.user_id,
        )
        new_workflow_id = 'notify-' + str(uuid.uuid4())
        notify = await add_notification(session, event.id, date_of_notify, new_workflow_id)
        return notify_workflow_schemas.NotifyData(notify_id=notify.id)


@activity.defn
async def send_notify_info(data: notify_workflow_schemas.NotifyData) -> None:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        notification = await notification_utils.get_notification(session, data.notify_id)
        if notification is None:
            raise RuntimeError(f'No notification {data.notify_id}')
        event = await event_utils.get_event(session=session, event_id=notification.event_id)
        if event is None:
            raise RuntimeError(f'No event {notification.event_id}')
        user = await user_utils.get_user_by_id(session=session, user_id=event.user_id)
        if user is None:
            raise RuntimeError(f'No user {event.user_id}')
    settings = config.get_settings()
    bot = aiogram.Bot(token=settings.TG_BOT_TOKEN.get_secret_value())

    # TODO as is warning
    # TODO user timezone
    text = f'Напомним о событии\n"{event.name}"\nв {notification.notify_ts.isoformat()}'
    await bot.send_message(chat_id=user.tg_id, text=text, reply_markup=notify_markup.get_keyboard(event_id=event.id))


@workflow.defn(name='process-message-workflow', sandboxed=False)
class ProcessMessageWorkflow:
    @workflow.run
    async def run(self, data: process_message_workflow_schemas.MessageInfo) -> None:
        gpt_json = validate_json(data)
        loguru.logger.info('GPT JSON: {}', gpt_json)
        if not gpt_json:
            data.gpt_json = AsIsJson(data)
        else:
            data.gpt_json = gpt_json
        loguru.logger.info('Validated JSON: {}', data)

        data = typing.cast(process_message_workflow_schemas.MessageInfoRequired, data)

        add_event_process_result: notify_workflow_schemas.NotifyData = await workflow.execute_activity(
            add_event_process, data, start_to_close_timeout=timedelta(seconds=30)
        )
        loguru.logger.info('add_event_process_result: {}', add_event_process_result)

        add_new_workflow_result = await workflow.execute_activity(
            add_new_workflow, add_event_process_result, start_to_close_timeout=timedelta(seconds=30)
        )
        loguru.logger.info('add_new_workflow_result: {}', add_new_workflow_result)

        await workflow.execute_activity(
            send_notify_info, add_event_process_result, start_to_close_timeout=timedelta(seconds=30)
        )
        loguru.logger.info('send_notify_info_result')
