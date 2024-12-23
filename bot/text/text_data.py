from enum import Enum


class TextData(str, Enum):
    ACTION_CANCEL = 'Действие отменено'

    EVENT_CREATED = '✅ Событие успешно создано!'
    EVENT_INFO = """
✨ Событие: {name}
⏳ Время события: {event_time}
📨 Следующее напоминание: {next_notify_time}
""".strip()
    EVENT_CREATED_AS_IS = 'Не смогли распознать напоминание, поэтому сохранили исходное сообщение'

    MSG_EVENT_CREATED = EVENT_CREATED + '\n\n' + EVENT_INFO
    MSG_EVENT_CREATED_AS_IS = EVENT_CREATED_AS_IS + '\n\n' + EVENT_INFO
    MSG_NOTIFY = """🔔 Напоминание! 🔔

📢 Событие: {name}
📅 Время события: {event_time}
📨 Следующее напоминание: {next_notify_time}
""".strip()
    MSG_START = 'Hello!'  # TODO

    MSG_TIMEZONE_LOC_ERROR = 'Не удалось определить ваш часовой пояс по геолокации. Попробуйте ввести таймзону вручную'
    MSG_TIMEZONE_CHANGE_OK = 'Таймзона успешно обновлена. Текущий часовой пояс: {offset}'
