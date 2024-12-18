import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .send_notify import send_reminder, ReminderWorkflow

async def main():
    # Подключение к Temporal серверу
    client = await Client.connect("localhost:7233")

    # Запуск воркера
    async with Worker(
        client,
        task_queue="reminder-timestamp-task-queue",
        workflows=[ReminderWorkflow],
        activities=[send_reminder],
    ):
        print("Worker запущен и ожидает задачи...")

        # Указываем имя и timestamp (UNIX time), когда должно быть отправлено сообщение
        text = "Погулять с собакой"
        send_timestamp = int(
            1734507300
        )

        # Запуск Workflow с указанным временем
        await client.start_workflow(
            ReminderWorkflow.run,
            text,
            send_timestamp,
            id="reminder-timestamp-workflow-id",
            task_queue="reminder-timestamp-task-queue",
        )

        print("Workflow запущен. Ждём выполнения...")

        # Чтобы worker не останавливался
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
