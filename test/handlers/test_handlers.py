from unittest import TestCase
from unittest.mock import patch, call

from telegram import ParseMode
from src.handlers import (
    send_reminder,
    add_meal_handler,
    history_handler,
    skip_handler,
)
from src.exceptions import NoMealConfigured
from test.base import get_mock_context, get_mock_update


class HandlerTest(TestCase):
    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("src.handlers.handlers.get_skip", side_effect=[None])
    @patch(
        "src.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 4)],
    )
    @patch("src.handlers.handlers.add_history")
    def test_send_reminder(self, *args):
        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_called_once_with(
            "",
            "Hola `test name` te toca comprar los ingredientes para hacer `test meal`",
            parse_mode=ParseMode().MARKDOWN_V2,
        )

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("src.handlers.handlers.get_skip", side_effect=[None])
    @patch(
        "src.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 4)],
    )
    @patch("src.handlers.handlers.add_history")
    def test_send_reminder_add_history(self, addhistoryfn, *args):
        context = get_mock_context()
        send_reminder(context)

        addhistoryfn.assert_called_once_with("test name")

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("src.handlers.handlers.get_skip", side_effect=[None])
    @patch(
        "src.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 0)],
    )
    @patch("src.handlers.handlers.add_history")
    def test_send_reminder_no_more_meals(self, *args):
        context = get_mock_context()
        send_reminder(context)

        self.assertEqual(2, context.bot.send_message.call_count)
        context.bot.send_message.assert_has_calls(
            [
                call(
                    "",
                    "Hola `test name` te toca comprar los ingredientes para hacer `test meal`",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
                call(
                    "",
                    "Además les informo que no hay más comidas configuradas, ponganse a pensar",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
            ]
        )

    def no_meal_configured():
        raise NoMealConfigured()

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("src.handlers.handlers.get_skip", side_effect=[None])
    @patch("src.handlers.handlers.get_next_meal", side_effect=no_meal_configured)
    def test_send_reminder_no_meal(self, *args):
        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_called_once_with(
            "",
            "Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas.",
        )

    @patch.dict("os.environ", {"CHAT_ID": "1"})
    @patch("src.handlers.commands.add_meal")
    def test_add_meal_handler(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        add_meal_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Ahí le agregué la comida `meal` a `name`", parse_mode=ParseMode.MARKDOWN_V2
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

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("src.handlers.handlers.get_skip", side_effect=["skip"])
    @patch(
        "src.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 0)],
    )
    @patch("src.handlers.handlers.add_history")
    def test_send_reminder_skip_active(self, history_call, get_next_meal_call, *args):
        context = get_mock_context()
        send_reminder(context)

        self.assertFalse(history_call.called)
        self.assertFalse(get_next_meal_call.called)

        self.assertEqual(0, context.bot.send_message.call_count)

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

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("src.handlers.handlers.get_skip", side_effect=["skip", None])
    @patch(
        "src.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 0)],
    )
    @patch("src.handlers.handlers.add_history")
    def test_send_reminders_skip_active(self, history_call, get_next_meal_call, *args):
        context = get_mock_context()
        send_reminder(context)

        self.assertFalse(history_call.called)
        self.assertFalse(get_next_meal_call.called)

        self.assertEqual(0, context.bot.send_message.call_count)

        send_reminder(context)

        self.assertTrue(history_call.called)
        self.assertTrue(get_next_meal_call.called)

        self.assertEqual(2, context.bot.send_message.call_count)

    @patch.dict("os.environ", {"CHAT_ID": "2"})
    def test_skip_handler_unknown_chat(self, *args):
        context = get_mock_context(["name", "meal"])
        update = get_mock_update()
        skip_handler(update, context)

        update.message.reply_photo.assert_called_once_with(
            "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
        )
