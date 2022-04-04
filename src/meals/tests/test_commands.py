from datetime import datetime
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.utils import timezone
from meals.tests.factories import MealFactory, MealItemFactory, ParticipantFactory
from meals.models import Meal, MealItem, Participant, Skip
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
            "Hay usuarios inválidos, los válidos son:\n\\- test\n\\- test2"
        )

    @override_settings(CHAT_ID=1)
    def test_meal_is_added_existing_participant(self):
        ParticipantFactory(name="existing")
        context = get_mock_context(["existing", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        self.assertEquals(Participant.objects.count(), 1)
        self.assertEquals(Participant.objects.first().name, "existing")
        self.assertEquals(Meal.objects.first().done, False)
        self.assertEquals(MealItem.objects.first().description, "meal")
        update.message.reply_text.assert_called_once_with(
            "Ahí agregué la comida: `meal` a cargo de *existing*"
        )

    @override_settings(CHAT_ID=1)
    def test_meal_is_added_existing_participant_with_uppercase(self):
        ParticipantFactory(name="existing")
        context = get_mock_context(["Existing", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        self.assertEquals(Participant.objects.count(), 1)
        self.assertEquals(Participant.objects.first().name, "existing")
        self.assertEquals(Meal.objects.first().done, False)
        self.assertEquals(Meal.objects.first().mealitem_set.first().description, "meal")

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
    def test_meal_is_added_existing_participants(self):
        ParticipantFactory(name="existing")
        ParticipantFactory(name="existing2")
        ParticipantFactory(name="existing3")
        context = get_mock_context(
            ["existing", "meal,", "existing2", "other meal,", "existing3", "dessert"]
        )
        update = get_mock_update()
        add_meal_handler(update, context)

        self.assertEquals(MealItem.objects.count(), 3)
        self.assertEquals(Meal.objects.count(), 1)
        self.assertEquals(Participant.objects.count(), 3)
        self.assertEquals(Participant.objects.all()[0].name, "existing")
        self.assertEquals(MealItem.objects.all()[0].description, "meal")
        self.assertEquals(Participant.objects.all()[1].name, "existing2")
        self.assertEquals(MealItem.objects.all()[1].description, "other meal")
        self.assertEquals(Participant.objects.all()[2].name, "existing3")
        self.assertEquals(MealItem.objects.all()[2].description, "dessert")
        update.message.reply_text.assert_called_once_with(
            "Ahí agregué la comida:\n\\- `meal` a cargo de *existing*\n\\- `other meal` a cargo de *existing2*\n\\- `dessert` a cargo de *existing3*"
        )

    @override_settings(CHAT_ID=1)
    def test_history_handler(self, *args):
        p1 = ParticipantFactory(name="test1")
        p2 = ParticipantFactory(name="test2")

        MealItemFactory(meal=MealFactory(done=True), owner=p1)
        MealItemFactory(meal=MealFactory(done=True), owner=p1)
        MealItemFactory(meal=MealFactory(done=True), owner=p2)
        context = get_mock_context()
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "El historial es: \n\n\\- *test1* compró para `2` comidas\\.\n\\- *test2* compró para `1` comida\\."
        )

    @override_settings(CHAT_ID=1)
    def test_history_handler_meal_with_multiple_items(self, *args):
        p1 = ParticipantFactory(name="test1")
        p2 = ParticipantFactory(name="test2")

        meal = MealFactory(done=True)
        MealItemFactory(meal=meal, owner=p1)
        MealItemFactory(meal=meal, owner=p2)
        MealItemFactory(meal=MealFactory(done=True), owner=p1)
        context = get_mock_context()
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "El historial es: \n\n\\- *test1* compró para `2` comidas\\.\n\\- *test2* compró para `1` comida\\."
        )

    @override_settings(CHAT_ID=2)
    def test_history_handler_unknown_chat(self, *args):
        p1 = ParticipantFactory(name="test1")
        p2 = ParticipantFactory(name="test2")

        MealItemFactory(meal=MealFactory(done=True), owner=p1)
        MealItemFactory(meal=MealFactory(done=True), owner=p1)
        MealItemFactory(meal=MealFactory(done=True), owner=p2)
        context = get_mock_context()
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "El historial es: \n\n\\- *test1* compró para `2` comidas\\.\n\\- *test2* compró para `1` comida\\."
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
    @override_settings(REMINDER_DAY=0)
    @patch(
        "meals.handlers.utils.timezone.now",
        side_effect=lambda: datetime.strptime(
            "2022-04-02 15:27:05.004573 -0300", "%Y-%m-%d %H:%M:%S.%f %z"
        ),
    )
    def test_next_meals_handler(self, *args):
        meal_item1 = MealItemFactory(
            description="test meal", owner=ParticipantFactory(name="test name")
        )
        meal = MealFactory()
        MealItemFactory(
            description="test meal2",
            meal=meal,
            owner=ParticipantFactory(name="test name2"),
        )
        MealItemFactory(
            description="test meal3",
            meal=meal,
            owner=ParticipantFactory(name="test name3"),
        )
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            f"""*Las próximas comidas son:*

martes 5 de abril _\\(id: {meal_item1.meal.id}\\)_
\t\\- `test meal` a cargo de *test name*

martes 12 de abril _\\(id: {meal.id}\\)_
\t\\- `test meal2` a cargo de *test name2*
\t\\- `test meal3` a cargo de *test name3*""",
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

        update.message.reply_text.assert_called_once_with("No hay próximas comidas\\.")

    @override_settings(CHAT_ID=1)
    def test_delete_first_meal_handler(self, *args):
        meal_item = MealItemFactory(
            owner=ParticipantFactory(name="test name"), description="test meal"
        )

        context = get_mock_context([meal_item.meal.id])
        update = get_mock_update()
        delete_meal_handler(update, context)

        self.assertEquals(0, Meal.objects.count())
        update.message.reply_text.assert_called_once_with(
            f"Borré la comida {meal_item.meal.id}\\.",
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
        meal_item = MealItemFactory(
            owner=ParticipantFactory(name="test name"), description="test meal"
        )

        context = get_mock_context([meal_item.meal.id])
        update = get_mock_update()
        resolve_meal_handler(update, context)

        meal_item.refresh_from_db()
        self.assertTrue(meal_item.meal.done)
        self.assertEquals(timezone.now().date(), meal_item.meal.done_at)
        update.message.reply_text.assert_called_once_with(
            f"Resolví la comida {meal_item.meal.id}\\.",
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
