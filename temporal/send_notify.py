from dataclasses import dataclass
from datetime import datetime, timedelta
from temporalio import activity, workflow


@dataclass
class ReminderInput:
    text: str


@activity.defn
async def send_reminder(input: ReminderInput) -> str:
    """
    Пример активити: компонуем сообщение.
    """
    return f"""Новое напоминание!
{input.text}"""


@workflow.defn
class ReminderWorkflow:
    @workflow.run
    async def run(self, text: str, send_timestamp: int) -> None:
        """
        Workflow ждёт до указанного времени (send_timestamp) и отправляет приветствие.
        """
        # Переводим timestamp в datetime
        target_time = datetime.fromtimestamp(send_timestamp)
        workflow.logger.info("Workflow будет спать до: %s", target_time)

        # Спим до нужного времени
        await workflow.sleep_until(target_time)

        # Выполняем активити
        result = await workflow.execute_activity(
            send_reminder,
            ReminderInput(text),
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info("Result: %s", result)



