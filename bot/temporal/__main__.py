import asyncio

import loguru
from temporalio.client import Client
from temporalio.worker import Worker

from bot import config, logger_config

from .notify_workflow import NotificationWorkflow, add_new_workflow, send_notify, update_db
from .process_message_workflow import ProcessMessageWorkflow, add_event_process, send_notify_info
from .set_delay_workflow import ProcessDelayWorkflow, new_notify_process, send_update_info


async def main() -> None:
    # Подключение к Temporal серверу
    client = await Client.connect('temporal:7233')

    settings = config.get_settings()
    logger_config.configure_logger(settings, log_file=settings.LOGGING_WORKER_FILE, application='worker')

    # Запуск воркера
    async with Worker(
        client,
        task_queue='reminder-workflow-task-queue',
        workflows=[NotificationWorkflow, ProcessMessageWorkflow, ProcessDelayWorkflow],
        activities=[
            send_notify,
            update_db,
            add_new_workflow,
            add_event_process,
            send_notify_info,
            new_notify_process,
            send_update_info,
        ],
    ):
        loguru.logger.info('Worker запущен и ожидает задачи...')
        # Чтобы worker не останавливался
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
