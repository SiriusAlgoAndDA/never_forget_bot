# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, fuzzy

from bot.database.models import User


class UserFactory(Factory):
    class Meta:
        model = User

    tg_id = fuzzy.FuzzyText()
    tg_username = fuzzy.FuzzyText()
    tg_name = fuzzy.FuzzyText()
    timezone = fuzzy.FuzzyFloat(0, 1)
