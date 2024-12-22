import json
import uuid

import loguru
import temporalio.client

from bot.database import models
from bot.schemas.process_message_workflow import process_message_workflow_schemas
from bot.utils.gpt import yandex_gpt


async def process_message(text: str, user: models.User, iam_token: str | None = None) -> None:
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
            gpt_json=json_result, message_text=text, user_id=user.id, user_tz=user.timezone
        ),
        id=workflow_id,
        task_queue='reminder-workflow-task-queue',
    )
    loguru.logger.info('Workflow {} started', workflow_id)
