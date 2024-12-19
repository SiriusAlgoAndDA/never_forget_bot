import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .send_notify import send_reminder, ReminderWorkflow

async def main():
    # Подключение к Temporal серверу
    client = await Client.connect("temporal:7233")

    # Запуск воркера
    async with Worker(
        client,
        task_queue="reminder-timestamp-task-queue",
        workflows=[ReminderWorkflow],
        activities=[send_reminder],
    ):
        print("Worker запущен и ожидает задачи...")
        # Чтобы worker не останавливался
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
