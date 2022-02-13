from django.test import TestCase
from unittest.mock import patch

from meals.models import Meal, Participant
from meals.handlers import (
    add_meal_handler,
    history_handler,
    skip_handler,
    next_meals_handler,
    delete_meal_handler,
)
from meals.tests.base import get_mock_context, get_mock_update, no_meal_configured


def get_history_mock():
    class MockParticipant:
        def __init__(self, name, total_meals):
            self.name = name
            self.total_meals = total_meals

    return [MockParticipant("test1", 2), MockParticipant("test2", 1)]


class CommandsTest(TestCase):
    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("meals.handlers.commands.add_meal")
    def test_add_meal_handler(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Ahí le agregué la comida `meal` a *name*\\."
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("meals.handlers.handlers.get_next_meal", side_effect=no_meal_configured)
    def test_add_meal_handler_no_args(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Para que pueda agregar necesito que me pases un nombre y una comida\\."
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    @patch("meals.handlers.handlers.get_next_meal", side_effect=no_meal_configured)
    def test_add_meal_handler_unknown_chat(self, *args):
        context = get_mock_context([1, 2])
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("meals.handlers.commands.history", side_effect=[get_history_mock()])
    def test_history_handler(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "El historial es: \n\n\\- *test1* hizo `2` comidas\\.\n\\- *test2* hizo `1` comida\\."
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    @patch("meals.handlers.commands.history", side_effect=[[]])
    def test_history_handler_unknown_chat(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("meals.handlers.commands.add_skip")
    def test_skip_handler(self, skip_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        skip_handler(update, context)

        self.assertTrue(skip_call.called)
        update.message.reply_text.assert_called_once_with(
            "Perfecto, me salteo una comida\\."
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    def test_skip_handler_unknown_chat(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        skip_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch(
        "meals.handlers.commands.get_next_meals",
        side_effect=[
            [
                (
                    "test name",
                    "test meal",
                    "1",
                ),
                ("test name2", "test meal2", "2"),
            ]
        ],
    )
    def test_next_meals_handler(self, get_next_meals_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        self.assertTrue(get_next_meals_call.called)
        update.message.reply_text.assert_called_once_with(
            """Las próximas comidas son:
\\- `test meal` a cargo de *test name* \\(id: 1\\)\\.
\\- `test meal2` a cargo de *test name2* \\(id: 2\\)\\.
""",
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("meals.handlers.commands.get_next_meals", side_effect=[[]])
    def test_next_meals_handler_no_meals(self, get_next_meals_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        self.assertTrue(get_next_meals_call.called)
        update.message.reply_text.assert_called_once_with("No hay próximas comidas\\.")

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    def test_next_meals_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch(
        "meals.handlers.commands.delete_meal",
        side_effect=[("test name", "test meal")],
    )
    def test_delete_first_meal_handler(self, delete_meal_call, *args):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"), description="test"
        )

        context = get_mock_context(["1"])
        update = get_mock_update()
        delete_meal_handler(update, context)

        self.assertTrue(delete_meal_call.called)
        update.message.reply_text.assert_called_once_with(
            "Borré la comida `test meal` a cargo de *test name*\\.",
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    def test_delete_meal_handler_no_meals(self, *args):
        context = get_mock_context(["1"])
        update = get_mock_update()
        delete_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Nada que borrar, no hay comida con id 1\\.",
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    def test_delete_meal_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        delete_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )
