from unittest import TestCase
from unittest.mock import patch, call

from telegram import ParseMode
from src.handlers import (
    send_reminder,
    reply_to_coca_handler,
)
from test.base import get_mock_context, no_meal_configured, get_mock_update


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

    @patch.dict("os.environ", {"CHAT_ID": ""})
    def test_reply_to_coca_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        reply_to_coca_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Soy una entidad virtual, no me contestes", quote=False
        )
