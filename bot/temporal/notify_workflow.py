import uuid
from datetime import datetime, timedelta, timezone

import aiogram
import loguru
from temporalio import activity, workflow
from temporalio.client import Client

from bot import config
from bot.database.connection import SessionManager
from bot.markups import notify_markup
from bot.schemas.event import event_schemas
from bot.schemas.notification import notification_schemas
from bot.schemas.notify_workflow import notify_workflow_schemas
from bot.text import text_data
from bot.utils import user_utils
from bot.utils.common import datetime_utils
from bot.utils.common.datetime_utils import utcnow
from bot.utils.event_utils import get_event
from bot.utils.notification_utils import add_notification, get_notification, update_notification_status, update_sent_ts


settings = config.get_settings()


@activity.defn
async def send_notify(data: notify_workflow_schemas.NotifyData) -> str | notify_workflow_schemas.NotifyDataSent:
    bot = aiogram.Bot(token=settings.TG_BOT_TOKEN.get_secret_value())
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        notify = await get_notification(session, data.notify_id)
        if notify is None:
            return 'Notification is None'
        if notify.status != notification_schemas.NotificationStatus.PENDING:
            return 'Notification Status is not pending'
        event = await get_event(session, notify.event_id)
        if event is None:
            return 'Event is None'
        if event.status != event_schemas.EventStatus.PENDING:
            await update_notification_status(session, notify.id, notification_schemas.NotificationStatus.CANCELLED)
            return 'Event is closed'
        user = await user_utils.get_user_by_id(session, event.user_id)
        if user is None:
            return 'User is None'

        event_ts = event.time.astimezone(tz=timezone(timedelta(hours=user.timezone)))
        next_notify_ts = (datetime_utils.utcnow() + event.reschedule_timedelta).astimezone(
            tz=timezone(timedelta(hours=user.timezone))
        )

        text: str = text_data.TextData.MSG_NOTIFY
        text = text.format(
            name=event.name.capitalize(),
            event_time=event_ts.strftime('%H:%M:%S %d.%m.%Y'),
            next_notify_time=next_notify_ts.strftime('%H:%M:%S %d.%m.%Y'),
        )

        msg = await bot.send_message(
            chat_id=user.tg_id,
            text=text,
            disable_web_page_preview=False,
            parse_mode=None,
            reply_markup=notify_markup.get_keyboard(event_id=event.id),
        )
        return notify_workflow_schemas.NotifyDataSent(notify.id, msg.date.isoformat())


@activity.defn
async def update_db(data: notify_workflow_schemas.NotifyDataSent) -> str | notify_workflow_schemas.NotifyData:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        await update_notification_status(session, data.notify_id, notification_schemas.NotificationStatus.SENT)
        await update_sent_ts(session, data.notify_id, datetime.fromisoformat(data.sent_ts))
        notify = await get_notification(session, data.notify_id)
        if notify is None:
            return 'Notification is None'
        event = await get_event(session, notify.event_id)
        if event is None:
            return 'Event is None'
        user = await user_utils.get_user_by_id(session, event.user_id)
        if user is None:
            return 'User is None'
        new_notify_ts = datetime.fromisoformat(data.sent_ts) + event.reschedule_timedelta
        new_workflow_id = 'notify-' + str(uuid.uuid4())
        new_notify = await add_notification(session, notify.event_id, new_notify_ts, new_workflow_id)
        return notify_workflow_schemas.NotifyData(new_notify.id)


@activity.defn
async def add_new_workflow(data: notify_workflow_schemas.NotifyData) -> str:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        notify = await get_notification(session, data.notify_id)
        if notify is None:
            return 'Notification is None'
        workflow_id = notify.workflow_id
        client = await Client.connect('temporal:7233')
        send_delay = notify.notify_ts - utcnow()
        send_delay = max(send_delay, timedelta(seconds=0))
        loguru.logger.info('Send delay: {}', send_delay)
        await client.start_workflow(
            'notification-workflow',
            notify_workflow_schemas.NotifyData(notify.id),
            id=workflow_id,
            task_queue='reminder-workflow-task-queue',
            start_delay=send_delay,
        )
        loguru.logger.info('Workflow {} will execute at {}', workflow_id, utcnow() + send_delay)
        return 'Success'


@workflow.defn(name='notification-workflow', sandboxed=False)
class NotificationWorkflow:
    @workflow.run
    async def run(self, data: notify_workflow_schemas.NotifyData) -> None:
        # Выполняем активити
        result = await workflow.execute_activity(send_notify, data, start_to_close_timeout=timedelta(seconds=30))
        loguru.logger.info('Sent message: {}\nNotify_id: {}', result, data.notify_id)
        if isinstance(result, str):
            return
        update_db_result: str | notify_workflow_schemas.NotifyData = await workflow.execute_activity(
            update_db, result, start_to_close_timeout=timedelta(seconds=30)
        )
        if isinstance(update_db_result, str):
            return
        loguru.logger.info('Update db\nNotify_old_id: {}\nNotify New ID', data.notify_id, update_db_result.notify_id)
        result = await workflow.execute_activity(
            add_new_workflow, update_db_result, start_to_close_timeout=timedelta(seconds=30)
        )
        loguru.logger.info('Worker add: {}', result)
