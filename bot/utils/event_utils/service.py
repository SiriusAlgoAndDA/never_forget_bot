import json
import uuid
from datetime import timedelta

import loguru
import temporalio.client
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models
from bot.database.connection import SessionManager
from bot.schemas.event.set_delay_workflow.set_delay_workflow_schema import SetDelayInfo
from bot.schemas.notification import notification_schemas
from bot.schemas.process_message_workflow import process_message_workflow_schemas
from bot.utils.event_utils.database import update_event_status
from bot.utils.gpt import yandex_gpt
from bot.utils.notification_utils.database import get_active_notification_by_event_id, update_notification_status


async def process_message(text: str, user: models.User, message_id: int, iam_token: str | None = None) -> None:
    gpt_data = await yandex_gpt.request_to_gpt(text, user, iam_token=iam_token)
    json_result = None
    try:
        json_result = json.loads(gpt_data)
    except json.JSONDecodeError:
        loguru.logger.exception('Failed to parse json')
    loguru.logger.info('Creating workflow')
    workflow_id = 'process-message-' + str(uuid.uuid4())
    client = await temporalio.client.Client.connect('temporal:7233')
    await client.start_workflow(
        'process-message-workflow',
        process_message_workflow_schemas.MessageInfo(
            gpt_json=json_result, message_text=text, user_id=user.id, user_tz=user.timezone, message_id=message_id
        ),
        id=workflow_id,
        task_queue='reminder-workflow-task-queue',
    )
    loguru.logger.info('Workflow {} started', workflow_id)


async def set_finish_status(session: AsyncSession, event_id: uuid.UUID | str, status: str) -> None:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        await update_event_status(session, event_id, status)
        notifications = await get_active_notification_by_event_id(session, event_id)
        for notify in notifications:
            await update_notification_status(session, notify.id, notification_schemas.NotificationStatus.CANCELLED)


async def set_delay(event_id: uuid.UUID | str, delta: timedelta, tg_id: int, msg_id: int) -> None:
    loguru.logger.info('Creating workflow')
    workflow_id = 'process-delay-' + str(uuid.uuid4())
    client = await temporalio.client.Client.connect('temporal:7233')
    await client.start_workflow(
        'process-delay-workflow',
        SetDelayInfo(str(event_id), int(delta.total_seconds()), msg_id, tg_id),
        id=workflow_id,
        task_queue='reminder-workflow-task-queue',
    )
    loguru.logger.info('Workflow {} started', workflow_id)
