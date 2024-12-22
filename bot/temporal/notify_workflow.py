import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiogram
from temporalio import activity, workflow
from temporalio.client import Client

from bot import config
from bot.database.connection import SessionManager
from bot.utils.common.datetime_utils import utcnow
from bot.utils.event_utils import get_event
from bot.utils.notification_utils import (
    NotificationStatus,
    add_notification,
    get_notification,
    update_notification_status,
    update_sent_ts,
)
from bot.utils.user_utils import get_user_by_id


settings = config.get_settings()


@dataclass
class Notifydata:
    notify_id: uuid.UUID
    sent_ts: datetime | None = None


@activity.defn
async def send_notify(data: Notifydata) -> str | Notifydata:
    bot = aiogram.Bot(token=settings.TG_BOT_TOKEN.get_secret_value())
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        notify = await get_notification(session, data.notify_id)
        if notify is None:
            return 'Notification is None'
        event = await get_event(session, notify.event_id)
        if event is None:
            return 'Event is None'
        user = await get_user_by_id(session, event.user_id)
        if user is None:
            return 'User is None'
        msg = await bot.send_message(
            chat_id=user.tg_id, text=event.name, disable_web_page_preview=False, parse_mode=None
        )
        return Notifydata(notify.id, msg.date.isoformat())


@activity.defn
async def update_db(data: Notifydata) -> str | Notifydata:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        notify = await update_notification_status(session, data.notify_id, NotificationStatus.SENT)
        notify = await update_sent_ts(session, data.notify_id, datetime.fromisoformat(data.sent_ts))
        if notify is None:
            return 'Notification is None'
        event = await get_event(session, notify.event_id)
        if event is None:
            return 'Event is None'
        user = await get_user_by_id(session, event.user_id)
        if user is None:
            return 'User is None'
        new_notify_ts = datetime.fromisoformat(data.sent_ts) + event.reschedule_timedelta
        new_workflow_id = 'notify-' + str(uuid.uuid4())
        new_notify = await add_notification(session, notify.event_id, new_notify_ts, new_workflow_id)
        return Notifydata(new_notify.id)


@activity.defn
async def add_new_workflow(data: Notifydata) -> str:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        notify = await get_notification(session, data.notify_id)
        if notify is None:
            return 'Notification is None'
        workflow_id = notify.workflow_id
        client = await Client.connect('temporal:7233')
        send_delay = notify.notify_ts - utcnow()
        if send_delay < timedelta(seconds = 0):
            send_delay = timedelta(seconds= 0)
        await client.start_workflow(
            'notification-workflow',
            Notifydata(notify.id),
            id=workflow_id,
            task_queue='reminder-workflow-task-queue',
            start_delay=send_delay,
        )
        return 'Success'


@workflow.defn(name='notification-workflow', sandboxed=False)
class NotificationWorkflow:
    @workflow.run
    async def run(self, data: Notifydata) -> None:
        # Выполняем активити
        result = await workflow.execute_activity(send_notify, data, start_to_close_timeout=timedelta(seconds=30))
        workflow.logger.info('Sent message: %s\nNotify_id: %s', result, data.notify_id)
        if result is str:
            return
        result: str | Notifydata = await workflow.execute_activity(update_db, result, start_to_close_timeout=timedelta(seconds=30))
        workflow.logger.info('Update db\nNotify_old_id: %s \nNotify New ID', data.notify_id, result.notify_id)
        if result is str:
            return
        result = await workflow.execute_activity(add_new_workflow, result, start_to_close_timeout=timedelta(seconds=30))
        workflow.logger.info('Worker add: ', result)
