# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from bot.database.models import Event


class EventFactory(Factory):
    class Meta:
        model = Event

    type = fuzzy.FuzzyText()
    name = fuzzy.FuzzyText()
    time = Faker('date_time')
    user_id = Faker('uuid4')
