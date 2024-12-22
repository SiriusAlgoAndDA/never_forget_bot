import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytimeparse
from temporalio import activity, workflow
from temporalio.client import Client

from bot.database.connection import SessionManager
from bot.temporal.notify_workflow import Notifydata, add_new_workflow
from bot.utils.event_utils import add_event
from bot.utils.notification_utils import add_notification
from bot.utils.user_utils import get_user_by_id

from copy import deepcopy


@dataclass
class MessageInfo:
    gpt_json: dict
    message_text: str
    user_id: uuid.UUID
    user_tz: int


def validate_json(info: MessageInfo) -> bool | dict:
    """{{
        "event": <event_name, str>,
        "date_of_event": <<time_of_event, hh:mm:ss> <date_of_event, dd.mm.yyyy>>,
        "date_of_notify": <<time_of_notify, hh:mm:ss> <date_of_notify, dd.mm.yyyy>>,
        "type_of_event": <type, str>,
        "repeat_interval": <interval, str or null>
    }}"""
    data = deepcopy(info.gpt_json)
    try:
        if type(data['event']) is not str:
            return False
        data['date_of_event'] = datetime.strptime(data['date_of_event'], '%H:%M:%S %d.%m.%Y').replace(
            timezone(timedelta(hours=info.user_tz))
        ).isoformat()
        data['date_of_notify'] = datetime.strptime(data['date_of_notify'], '%H:%M:%S %d.%m.%Y').replace(
            timezone(timedelta(hours=info.user_tz))
        ).isoformat()
        if data['type_of_event'] is not str:
            return False
        if data['repeat_interval'] is not None:
            data['repeat_interval'] = timedelta(seconds=pytimeparse.parse(data['repeat_interval']))
    except Exception as e:
        return False
    data['as_is'] = False
    return data


def AsIsJson(info: MessageInfo) -> dict:
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
async def add_event_process(data: MessageInfo) -> Notifydata:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        date_of_event = datetime.fromisoformat(data.gpt_json['date_of_event'])
        date_of_notify = datetime.fromisoformat(data.gpt_json['date_of_notify'])
        event = await add_event(session, data.gpt_json['type_of_event'], data.gpt_json['event'], date_of_event, data.user_id)
        new_workflow_id = 'notify-' + str(uuid.uuid4())
        notify = await add_notification(session, event.id, date_of_notify, new_workflow_id)
        return Notifydata( notify_id = notify.id)


async def create_event(data: dict, message_text :str, user_id: uuid.UUID, user_tz:int):
    workflow_id = "process-message-" + str(uuid.uuid4())
    client = await Client.connect('temporal:7233')
    await client.start_workflow(
        'process-message-workflow',
        MessageInfo(gpt_json=data, message_text = message_text, user_id=user_id, user_tz=user_tz),
        id=workflow_id,
        task_queue='reminder-workflow-task-queue'
    )

@workflow.defn(name='process-message-workflow', sandboxed=False)
class ProcessMessageWorkflow:
    @workflow.run
    async def run(self, data: MessageInfo) -> None:

        gpt_json = validate_json(data)
        workflow.logger.info('GPT JSON: %s\n', gpt_json) 
        if gpt_json == False:
            data.gpt_json = AsIsJson(data)
        else:
            data.gpt_json = gpt_json
        workflow.logger.info('GPT JSON: %s\n', data)
        result: Notifydata = await workflow.execute_activity(add_event_process, data, start_to_close_timeout=timedelta(seconds=30))
        workflow.logger.info('Add event: %s\n', result)
        result = await workflow.execute_activity(add_new_workflow, result, start_to_close_timeout=timedelta(seconds=30))
        workflow.logger.info('Add event: %s\n', result)
