import json
import uuid

import loguru
import temporalio.client
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import models
from bot.database.connection import SessionManager
from bot.schemas.process_message_workflow import process_message_workflow_schemas
from bot.utils.event_utils.database import update_event_status
from bot.utils.gpt import yandex_gpt
from bot.utils.notification_utils.database import (
    NotificationStatus,
    get_active_notification_by_event_id,
    update_notification_status,
)


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
            await update_notification_status(session, notify.id, NotificationStatus.CANCELLED)
