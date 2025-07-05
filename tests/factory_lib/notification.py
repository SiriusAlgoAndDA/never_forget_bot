# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from bot.database.models import Notification


class NotificationFactory(Factory):
    class Meta:
        model = Notification

    event_id = Faker('uuid4')
    notify_ts = Faker('date_time')
    sent_ts = Faker('date_time')
    status = fuzzy.FuzzyText()
    workflow_id = fuzzy.FuzzyText()
