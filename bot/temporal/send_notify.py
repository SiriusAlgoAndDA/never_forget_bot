import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiogram
from temporalio import activity, workflow
from temporalio.client import Client

from bot import config


settings = config.get_settings()
bot = aiogram.Bot(token=settings.TG_BOT_TOKEN.get_secret_value())


@dataclass
class Reminderdata:
    chat_id: int
    text: str


@activity.defn
async def send_reminder(data: Reminderdata) -> str:
    await bot.send_message(
        chat_id=data.chat_id,
        text=f"""Привет из Temporal!
{data.text}
""",
    )
    return f'Отправлено напоминание\nChat_id: {data.chat_id}\nText: {data.text}'


@workflow.defn(name='reminder-workflow', sandboxed=False)
class ReminderWorkflow:
    @workflow.run
    async def run(self, data: Reminderdata) -> None:
        # Выполняем активити
        result = await workflow.execute_activity(
            send_reminder,
            data,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info('Result: %s', result)


async def new_event(chat_id: int, event: str, timestamp: float) -> bool:
    client = await Client.connect('temporal:7233')
    now = datetime.now()
    execute_time = datetime.fromtimestamp(timestamp)
    if execute_time < now:
        return False
    time_delta = execute_time - now
    await client.start_workflow(
        'reminder-workflow',
        Reminderdata(chat_id, event),
        id='reminder-' + str(uuid.uuid4()),
        task_queue='reminder-timestamp-task-queue',
        start_delay=time_delta,
    )
    return True
