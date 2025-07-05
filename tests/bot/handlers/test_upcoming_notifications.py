from bot.handlers.upcoming_notifications import upcoming_notifications
from tests.factory_lib import user


async def test_upcoming_notifications_handler_empty(session, message, state) -> None:
    """Тест обработчика для случая, когда у пользователя нет уведомлений."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    # Вызываем обработчик
    await upcoming_notifications(message, user_obj, state)

    # Проверяем, что состояние очищено
    state.clear.assert_called_once()

    # Проверяем, что отправлено сообщение об отсутствии уведомлений
    message.reply.assert_called_once_with(text='Нет предстоящих уведомлений')


async def test_upcoming_notifications_handler_with_notifications(
    session, message, state, create_test_events_with_notifications
):
    """Тест обработчика для случая с уведомлениями."""
    user_obj = user.UserFactory()
    session.add(user_obj)
    await session.commit()

    await create_test_events_with_notifications(session, user_obj)

    # Вызываем обработчик
    await upcoming_notifications(message, user_obj, state)

    # Проверяем, что состояние очищено
    state.clear.assert_called_once()

    # Проверяем, что reply был вызван дважды (для каждого события)
    assert message.reply.call_count == 2

    # Проверяем порядок вызовов - первым должно быть событие 2 (уведомление раньше)
    calls = message.reply.call_args_list

    # Проверяем, что в первом вызове есть "Событие 2"
    first_call_text = calls[0][1]['text']
    assert 'Событие 2' in first_call_text

    # Проверяем, что во втором вызове есть "Событие 1"
    second_call_text = calls[1][1]['text']
    assert 'Событие 1' in second_call_text
