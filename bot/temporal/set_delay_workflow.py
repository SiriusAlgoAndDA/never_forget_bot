# pylint: disable=duplicate-code
import uuid
from datetime import timedelta, timezone

import aiogram
import loguru
from sqlalchemy import asc, select
from temporalio import activity, workflow

from bot import config
from bot.database import models
from bot.database.connection import SessionManager
from bot.schemas.event.set_delay_workflow.set_delay_workflow_schema import SetDelayInfo
from bot.schemas.notification import notification_schemas
from bot.schemas.notify_workflow import notify_workflow_schemas
from bot.utils import event_utils, notification_utils, user_utils
from bot.utils.notification_utils import add_notification
from bot.utils.notification_utils.database import get_active_notification_by_event_id, update_notification_status

from ..text import text_data
from .notify_workflow import add_new_workflow


@activity.defn
async def new_notify_process(
    data: SetDelayInfo,
) -> notify_workflow_schemas.NotifyData:
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        stmt = (
            select(models.Notification)
            .where(
                models.Notification.event_id == data.event_id,
                models.Notification.status == notification_schemas.NotificationStatus.PENDING,
            )
            .order_by(asc(models.Notification.notify_ts))  # Сортировка по notify_ts
            .limit(1)  # Берем только одно уведомление с минимальным временем
        )

        # Выполняем запрос
        last = await session.scalar(stmt)
        if last is None:
            return notify_workflow_schemas.NotifyData(notify_id='')
        date_of_notify = last.notify_ts + timedelta(seconds=data.delta)
        notifications = await get_active_notification_by_event_id(session, data.event_id)
        for notify in notifications:
            await update_notification_status(session, notify.id, notification_schemas.NotificationStatus.CANCELLED)
        new_workflow_id = 'notify-' + str(uuid.uuid4())
        notify = await add_notification(session, data.event_id, date_of_notify, new_workflow_id)
        return notify_workflow_schemas.NotifyData(notify_id=notify.id)


@activity.defn
async def send_update_info(data: notify_workflow_schemas.NotifyDataForCreated) -> None:
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

    event_ts = event.time.astimezone(tz=timezone(timedelta(hours=user.timezone)))
    notify_ts = notification.notify_ts.astimezone(tz=timezone(timedelta(hours=user.timezone)))

    text = text_data.TextData.EVENT_INFO.format(
        name=event.name,
        event_time=event_ts.strftime('%H:%M:%S %d.%m.%Y'),
        next_notify_time=notify_ts.strftime('%H:%M:%S %d.%m.%Y'),
    )

    await bot.send_message(
        chat_id=user.tg_id,
        reply_to_message_id=data.message_id,
        text=text,
    )


@workflow.defn(name='process-delay-workflow', sandboxed=False)
class ProcessDelayWorkflow:
    @workflow.run
    async def run(self, data: SetDelayInfo) -> None:
        add_event_process_result: notify_workflow_schemas.NotifyData = await workflow.execute_activity(
            activity=new_notify_process, arg=data, start_to_close_timeout=timedelta(seconds=30)
        )
        loguru.logger.info('new_notify_process_result: {}', add_event_process_result)
        if not add_event_process_result.notify_id:
            return

        add_new_workflow_result = await workflow.execute_activity(
            add_new_workflow, add_event_process_result, start_to_close_timeout=timedelta(seconds=30)
        )
        loguru.logger.info('add_new_workflow_result: {}', add_new_workflow_result)

        await workflow.execute_activity(
            send_update_info,
            notify_workflow_schemas.NotifyDataForCreated(
                notify_id=add_event_process_result.notify_id, as_is=False, message_id=data.msg_id
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        loguru.logger.info('send_update_info_result')
