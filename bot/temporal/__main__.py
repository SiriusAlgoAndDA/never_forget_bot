import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .notify_workflow import NotificationWorkflow, add_new_workflow, send_notify, update_db
from .process_message_workflow import ProcessMessageWorkflow, add_event_process


async def main() -> None:
    # Подключение к Temporal серверу
    client = await Client.connect('temporal:7233')

    # Запуск воркера
    async with Worker(
        client,
        task_queue='reminder-workflow-task-queue',
        workflows=[NotificationWorkflow, ProcessMessageWorkflow],
        activities=[send_notify, update_db, add_new_workflow, add_event_process],
    ):
        print('Worker запущен и ожидает задачи...')
        # Чтобы worker не останавливался
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
