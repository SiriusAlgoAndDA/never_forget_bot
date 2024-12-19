import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .reminder_workflow import ReminderWorkflow, send_reminder


async def main() -> None:
    # Подключение к Temporal серверу
    client = await Client.connect('temporal:7233')

    # Запуск воркера
    async with Worker(
        client,
        task_queue='reminder-workflow-task-queue',
        workflows=[ReminderWorkflow],
        activities=[send_reminder],
    ):
        print('Worker запущен и ожидает задачи...')
        # Чтобы worker не останавливался
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
