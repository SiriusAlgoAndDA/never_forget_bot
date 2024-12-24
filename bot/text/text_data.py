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
    MSG_START = """Привет!👋🏻

Я Never Forget Bot – Telegram-бот, который поможет Вам не забывать о важных задачах и событиях.
С помощью меня вы сможете легко управлять своими напоминаниями и оставаться на связи с вашими делами 🗓️

Давай начнем!
Напиши мне или запиши голосовое сообщение о том, когда и о чем тебе надо напомнить, и я не подведу!"""
    MSG_HELP = (
        MSG_START
        + '\n\n'
        + """
Вот что я еще могу:

– Доступные команды:

- /start – Начать работу со мной
- /help – Вывод этого сообщения
- /change_timezone – Меняет активный часовой пояс, чтобы я всегда знал, когда вам напомнить
- /upcoming_events – Показывает активные события, чтобы вы могли быстро оценить свою загрузку

– Удобства при работе с напоминаниями:

Под каждым событием у вас будет 7 кнопок, которые помогут вам управлять поставленными задачами:

- +10 минут – Отложить напоминание на 10 минут
- +1 час – Отложить напоминание на 1 час
- +1 день – Отложить напоминание на 1 сутки
- Отложить на другое время – Отложите напоминание на другое подходящее время
- Выполнено – Пометьте задачу как выполненную
- Не сделано – Если задача не была выполнена, отметьте это
- Удалить – Удалите напоминание, если оно больше не нужно

Я здесь, чтобы сделать вашу жизнь более организованной и продуктивной. Начнем? 💪✨""".strip()
    )

    MSG_TIMEZONE_LOC_ERROR = 'Не удалось определить ваш часовой пояс по геолокации. Попробуйте ввести таймзону вручную'
    MSG_TIMEZONE_CHANGE_OK = 'Таймзона успешно обновлена. Текущий часовой пояс: {offset}'
