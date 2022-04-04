from django.test import TestCase, override_settings
from django.utils import timezone
from unittest.mock import call, MagicMock

from telegram import ParseMode
from meals.handlers import (
    send_reminder,
    send_history_resume,
    reply_to_coca_handler,
)
from meals.tests.factories import (
    MealFactory,
    MealItemFactory,
    ParticipantFactory,
    SkipFactory,
)
from meals.tests.base import get_mock_context, get_mock_update


class HandlerTest(TestCase):
    @override_settings(CHAT_ID="")
    def test_send_reminder(self, *args):
        mealitem = MealItemFactory(owner=ParticipantFactory(name="test name"))
        MealItemFactory()
        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_called_once_with(
            "",
            """Hola\\!\n\\- *test name* te toca comprar los ingredientes para hacer `test meal`\\.""",
            parse_mode=ParseMode().MARKDOWN_V2,
        )

        mealitem.refresh_from_db()
        self.assertTrue(mealitem.meal.done)
        self.assertEquals(timezone.now().day, mealitem.meal.done_at.day)

    @override_settings(CHAT_ID="")
    def test_get_next_meal_returns_first_undone_meal(self):
        MealItemFactory(
            owner=ParticipantFactory(name="test"),
            description="test",
            meal=MealFactory(done=True),
        )
        MealItemFactory(owner=ParticipantFactory(name="test2"), description="test2")

        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_has_calls(
            [
                call(
                    "",
                    """Hola\\!\n\\- *test2* te toca comprar los ingredientes para hacer `test2`\\.""",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
                call(
                    "",
                    "Además les informo que no hay más comidas configuradas, ponganse a pensar\\.",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
            ]
        )

    @override_settings(CHAT_ID="")
    def test_send_reminder_no_more_meals(self, *args):
        MealItemFactory(owner=ParticipantFactory(name="test name"))
        context = get_mock_context()
        send_reminder(context)

        self.assertEqual(2, context.bot.send_message.call_count)
        context.bot.send_message.assert_has_calls(
            [
                call(
                    "",
                    "Hola\\!\n\\- *test name* te toca comprar los ingredientes para hacer `test meal`\\.",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
                call(
                    "",
                    "Además les informo que no hay más comidas configuradas, ponganse a pensar\\.",
                    parse_mode=ParseMode().MARKDOWN_V2,
                ),
            ]
        )

    @override_settings(CHAT_ID="")
    def test_send_reminder_no_meal(self, *args):
        context = get_mock_context()
        send_reminder(context)

        context.bot.send_message.assert_called_once_with(
            "",
            "Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas\\.",
        )

    @override_settings(CHAT_ID="")
    def test_send_reminder_skip_active(self, *args):
        SkipFactory()
        context = get_mock_context()
        send_reminder(context)

        self.assertEqual(0, context.bot.send_message.call_count)

    @override_settings(CHAT_ID="")
    def test_send_reminders_skip_active(self, *args):
        SkipFactory()
        MealItemFactory()
        context = get_mock_context()
        send_reminder(context)

        self.assertEqual(0, context.bot.send_message.call_count)

        send_reminder(context)

        self.assertEqual(2, context.bot.send_message.call_count)

    @override_settings(CHAT_ID="", TELEGRAM_TOKEN="25:test")
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

    @override_settings(CHAT_ID="", TELEGRAM_TOKEN="25:test")
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

    @override_settings(CHAT_ID="")
    def test_reply_to_coca_handler_random_high(self, *args):
        import random

        random.seed(26)
        context = get_mock_context()
        update = get_mock_update()
        reply_to_coca_handler(update, context)

        update.message.reply_text.assert_not_called()

    @override_settings(CHAT_ID="")
    def test_send_history_resume(self, *args):
        p2 = ParticipantFactory(name="test2")
        p1 = ParticipantFactory(name="test")
        MealItemFactory(meal=MealFactory(done=True), owner=p2)
        MealItemFactory(meal=MealFactory(done=True), owner=p2)
        MealItemFactory(meal=MealFactory(done=True), owner=p1)

        context = get_mock_context()
        send_history_resume(context)

        context.bot.send_message.assert_called_once_with(
            "",
            "Hola, les dejo el resumen del histórico de compras: \n\n\\- *test2* compró para `2` comidas\\.\n\\- *test* compró para `1` comida\\.",
        )
