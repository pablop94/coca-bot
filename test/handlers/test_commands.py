from unittest import TestCase
from unittest.mock import patch

from telegram import ParseMode
from src.handlers import (
    add_meal_handler,
    history_handler,
    skip_handler,
    next_meals_handler,
    delete_meal_handler,
)
from test.base import get_mock_context, get_mock_update, no_meal_configured


class CommandsTest(TestCase):
    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("src.handlers.commands.add_meal")
    def test_add_meal_handler(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Ahí le agregué la comida `meal` a *name*", parse_mode=ParseMode.MARKDOWN_V2
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("src.handlers.handlers.get_next_meal", side_effect=no_meal_configured)
    def test_add_meal_handler_no_args(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Para que pueda agregar necesito que me pases un nombre y una comida"
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    @patch("src.handlers.handlers.get_next_meal", side_effect=no_meal_configured)
    def test_add_meal_handler_unknown_chat(self, *args):
        context = get_mock_context([1, 2])
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("src.handlers.commands.history", side_effect=[["test1", "test2", "test1"]])
    def test_history_handler(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "El historial es\n\ntest1: 2\ntest2: 1", parse_mode=ParseMode.MARKDOWN_V2
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    @patch("src.handlers.commands.history", side_effect=[["test1", "test2", "test1"]])
    def test_history_handler_unknown_chat(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        history_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("src.handlers.commands.add_skip")
    def test_skip_handler(self, skip_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        skip_handler(update, context)

        self.assertTrue(skip_call.called)
        update.message.reply_text.assert_called_once_with(
            "Perfecto, me salteo una comida", parse_mode=ParseMode.MARKDOWN_V2
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
        "src.handlers.commands.get_next_meals",
        side_effect=[
            [
                (
                    "test name",
                    "test meal",
                ),
                ("test name2", "test meal2"),
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
\\- `test meal` a cargo de *test name*\\.
\\- `test meal2` a cargo de *test name2*\\.
""",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("src.handlers.commands.get_next_meals", side_effect=[[]])
    def test_next_meals_handler_no_meals(self, get_next_meals_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        next_meals_handler(update, context)

        self.assertTrue(get_next_meals_call.called)
        update.message.reply_text.assert_called_once_with("No hay próximas comidas")

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
        "src.handlers.commands.get_next_meal",
        side_effect=[("test name", "test meal", 4)],
    )
    def test_delete_meal_handler(self, get_next_meal_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        delete_meal_handler(update, context)

        self.assertTrue(get_next_meal_call.called)
        update.message.reply_text.assert_called_once_with(
            "Borré la comida `test meal` a cargo de *test name*",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch(
        "src.handlers.commands.get_next_meal",
        side_effect=no_meal_configured,
    )
    def test_delete_meal_handler_no_meals(self, get_next_meal_call, *args):
        context = get_mock_context()
        update = get_mock_update()
        delete_meal_handler(update, context)

        self.assertTrue(get_next_meal_call.called)
        update.message.reply_text.assert_called_once_with(
            "Nada que borrar, no hay comidas.",
        )

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    def test_delete_meal_handler_unknown_chat(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        delete_meal_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )
