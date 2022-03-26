from django.test import TestCase, override_settings
from django.utils import timezone
from meals.tests.factories import MealFactory, ParticipantFactory
from meals.models import Meal, Participant, Skip
from meals.handlers import (
    add_meal_handler,
    history_handler,
    skip_handler,
    next_meals_handler,
    delete_meal_handler,
    resolve_meal_handler,
)
from meals.tests.base import get_mock_context, get_mock_update


class CommandsTest(TestCase):
    @override_settings(CHAT_ID=1)
    def test_add_meal_handler(self, *args):
        ParticipantFactory(name="test")
        ParticipantFactory(name="test2")
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        self.assertEquals(0, Meal.objects.count())
        self.assertEquals(2, Participant.objects.count())
        update.message.reply_text.assert_called_once_with(
            "*name* no es un usuario válido, los válidos son:\n\\- test\n\\- test2"
        )

    @override_settings(CHAT_ID=1)
    def test_meal_is_added_existing_participant(self):
        ParticipantFactory(name="existing")
        context = get_mock_context(["existing", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        self.assertEquals(Participant.objects.count(), 1)
        self.assertEquals(Participant.objects.first().name, "existing")
        self.assertEquals(Meal.objects.first().description, "meal")

    @override_settings(CHAT_ID=1)
    def test_meal_is_added_existing_participant_with_uppercase(self):
        ParticipantFactory(name="existing")
        context = get_mock_context(["Existing", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        self.assertEquals(Participant.objects.count(), 1)
        self.assertEquals(Participant.objects.first().name, "existing")
        self.assertEquals(Meal.objects.first().description, "meal")

    @override_settings(CHAT_ID=1)
    def test_add_meal_handler_no_args(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Para que pueda agregar necesito que me pases un nombre y una comida\\."
        )

    @override_settings(CHAT_ID=2)
    def test_add_meal_handler_unknown_chat(self, *args):
        context = get_mock_context([1, 2])
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @override_settings(CHAT_ID=1)
    def test_history_handler(self, *args):
        p1 = ParticipantFactory(name="test1")
        p2 = ParticipantFactory(name="test2")

        MealFactory(done=True, meal_owner=p1)
        MealFactory(done=True, meal_owner=p1)
        MealFactory(done=True, meal_owner=p2)
        context = get_mock_context()
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "El historial es: \n\n\\- *test1* compró para `2` comidas\\.\n\\- *test2* compró para `1` comida\\."
        )

    @override_settings(CHAT_ID=2)
    def test_history_handler_unknown_chat(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @override_settings(CHAT_ID=1)
    def test_skip_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        skip_handler(update, context)

        self.assertEquals(1, Skip.objects.count())
        update.message.reply_text.assert_called_once_with(
            "Perfecto, me salteo una comida\\."
        )

    @override_settings(CHAT_ID=2)
    def test_skip_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        skip_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @override_settings(CHAT_ID=1)
    def test_next_meals_handler(self, *args):
        meal1 = MealFactory(
            description="test meal", meal_owner=ParticipantFactory(name="test name")
        )
        meal2 = MealFactory(
            description="test meal2", meal_owner=ParticipantFactory(name="test name2")
        )
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            f"""Las próximas comidas son:
\\- `test meal` a cargo de *test name* \\(id: {meal1.id}\\)\\.
\\- `test meal2` a cargo de *test name2* \\(id: {meal2.id}\\)\\.
""",
        )

    @override_settings(CHAT_ID=1)
    def test_next_meals_handler_no_meals(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        update.message.reply_text.assert_called_once_with("No hay próximas comidas\\.")

    @override_settings(CHAT_ID=2)
    def test_next_meals_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @override_settings(CHAT_ID=1)
    def test_delete_first_meal_handler(self, *args):
        meal = MealFactory(
            meal_owner=ParticipantFactory(name="test name"), description="test meal"
        )

        context = get_mock_context([meal.id])
        update = get_mock_update()
        delete_meal_handler(update, context)

        self.assertEquals(0, Meal.objects.count())
        update.message.reply_text.assert_called_once_with(
            "Borré la comida `test meal` a cargo de *test name*\\.",
        )

    @override_settings(CHAT_ID=1)
    def test_delete_meal_handler_no_meals(self, *args):
        context = get_mock_context(["1"])
        update = get_mock_update()
        delete_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Nada que borrar, no hay comida con id 1\\.",
        )

    @override_settings(CHAT_ID=1)
    def test_delete_meal_handler_invalid_id(self, *args):
        context = get_mock_context(["asd"])
        update = get_mock_update()
        delete_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Para borrar necesito un id\\. Podes ver el id usando \\/proximas\\."
        )

    @override_settings(CHAT_ID=2)
    def test_delete_meal_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        delete_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @override_settings(CHAT_ID=1)
    def test_resolve_meal_handler(self, *args):
        meal = MealFactory(
            meal_owner=ParticipantFactory(name="test name"), description="test meal"
        )

        context = get_mock_context([meal.id])
        update = get_mock_update()
        resolve_meal_handler(update, context)

        meal.refresh_from_db()
        self.assertTrue(meal.done)
        self.assertEquals(timezone.now().date(), meal.done_at)
        update.message.reply_text.assert_called_once_with(
            "Resolví la comida `test meal` a cargo de *test name*\\.",
        )

    @override_settings(CHAT_ID=1)
    def test_resolve_meal_handler_no_meals(self, *args):
        context = get_mock_context(["1"])
        update = get_mock_update()
        resolve_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Nada que resolver, no hay comida con id 1\\.",
        )

    @override_settings(CHAT_ID=1)
    def test_resolve_meal_handler_invalid_id(self, *args):
        context = get_mock_context(["asd"])
        update = get_mock_update()
        resolve_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Para resolver necesito un id\\. Podes ver el id usando \\/proximas\\."
        )

    @override_settings(CHAT_ID=2)
    def test_resolve_meal_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        resolve_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )
