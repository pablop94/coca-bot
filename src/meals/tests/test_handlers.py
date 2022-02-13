from django.test import TestCase
from unittest.mock import patch, call, MagicMock

from telegram import ParseMode
from meals.handlers import (
    send_reminder,
    reply_to_coca_handler,
)
from meals.tests.base import get_mock_context, no_meal_configured, get_mock_update


class HandlerTest(TestCase):
    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("meals.handlers.handlers.get_skip", side_effect=[None])
    @patch(
        "meals.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 4)],
    )
    def test_send_reminder(self, *args):
        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_called_once_with(
            "",
            "Hola `test name` te toca comprar los ingredientes para hacer `test meal`\\.",
            parse_mode=ParseMode().MARKDOWN_V2,
        )

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("meals.handlers.handlers.get_skip", side_effect=[None])
    @patch(
        "meals.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 0)],
    )
    def test_send_reminder_no_more_meals(self, *args):
        context = get_mock_context()
        send_reminder(context)

        self.assertEqual(2, context.bot.send_message.call_count)
        context.bot.send_message.assert_has_calls(
            [
                call(
                    "",
                    "Hola `test name` te toca comprar los ingredientes para hacer `test meal`\\.",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
                call(
                    "",
                    "Además les informo que no hay más comidas configuradas, ponganse a pensar\\.",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
            ]
        )

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("meals.handlers.handlers.get_skip", side_effect=[None])
    @patch("meals.handlers.handlers.get_next_meal", side_effect=no_meal_configured)
    def test_send_reminder_no_meal(self, *args):
        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_called_once_with(
            "",
            "Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas\\.",
        )

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("meals.handlers.handlers.get_skip", side_effect=["skip"])
    @patch(
        "meals.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 0)],
    )
    def test_send_reminder_skip_active(self, get_next_meal_call, *args):
        context = get_mock_context()
        send_reminder(context)

        self.assertFalse(get_next_meal_call.called)

        self.assertEqual(0, context.bot.send_message.call_count)

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch("meals.handlers.handlers.get_skip", side_effect=["skip", None])
    @patch(
        "meals.handlers.handlers.get_next_meal",
        side_effect=[("test name", "test meal", 0)],
    )
    def test_send_reminders_skip_active(self, get_next_meal_call, *args):
        context = get_mock_context()
        send_reminder(context)

        self.assertFalse(get_next_meal_call.called)

        self.assertEqual(0, context.bot.send_message.call_count)

        send_reminder(context)

        self.assertTrue(get_next_meal_call.called)

        self.assertEqual(2, context.bot.send_message.call_count)

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch.dict("os.environ", {"TELEGRAM_TOKEN": "25:test"})
    def test_reply_to_coca_handler(self, *args):
        """El id de usuario del bot es la primera parte del token, antes de los :"""
        import random

        random.seed(1)
        context = get_mock_context()
        update = get_mock_update()

        update.message.reply_to_message = MagicMock()
        update.message.reply_to_message.from_user = MagicMock()
        update.message.reply_to_message.from_user.id = 25

        reply_to_coca_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Soy una entidad virtual, no me contestes\\."
        )

    @patch.dict("os.environ", {"CHAT_ID": ""})
    @patch.dict("os.environ", {"TELEGRAM_TOKEN": "25:test"})
    def test_reply_to_coca_handler_other_chat(self, *args):
        """El id de usuario del bot es la primera parte del token, antes de los :"""
        import random

        random.seed(1)
        context = get_mock_context()
        update = get_mock_update()

        update.message.reply_to_message = MagicMock()
        update.message.reply_to_message.from_user = MagicMock()
        update.message.reply_to_message.from_user.id = 27

        reply_to_coca_handler(update, context)

        update.message.reply_text.assert_not_called()

    @patch.dict("os.environ", {"CHAT_ID": ""})
    def test_reply_to_coca_handler_random_high(self, *args):
        import random

        random.seed(26)
        context = get_mock_context()
        update = get_mock_update()
        reply_to_coca_handler(update, context)

        update.message.reply_text.assert_not_called()