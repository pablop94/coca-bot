import random
from django.test import SimpleTestCase, override_settings
from unittest.mock import patch
from meals.handlers import (
    rica_handler,
    pegar_handler,
    chocolate_handler,
    intentar_handler,
)

from meals.tests.base import get_mock_context, get_mock_update


class AudioHandlers(SimpleTestCase):
    def setUp(self, *args):
        random.seed(1)

    @override_settings(CHAT_ID=1)
    def test_rica_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        rica_handler(update, context)

        update.message.reply_audio.assert_called_once()

    @override_settings(CHAT_ID=1)
    @patch("meals.decorators.random.randint", side_effect=[51])
    def test_rica_handler_random_51(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        rica_handler(update, context)

        update.message.reply_audio.assert_not_called()

    @override_settings(CHAT_ID=1)
    def test_pegar_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        pegar_handler(update, context)

        update.message.reply_audio.assert_called_once()

    @override_settings(CHAT_ID=1)
    @patch("meals.decorators.random.randint", side_effect=[51])
    def test_pegar_handler_random_51(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        pegar_handler(update, context)

        update.message.reply_audio.assert_not_called()

    @override_settings(CHAT_ID=1)
    def test_chocolate_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        chocolate_handler(update, context)

        update.message.reply_audio.assert_called_once()

    @override_settings(CHAT_ID=1)
    @patch("meals.decorators.random.randint", side_effect=[51])
    def test_chocolate_handler_random_51(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        chocolate_handler(update, context)

        update.message.reply_audio.assert_not_called()

    @override_settings(CHAT_ID=1)
    def test_intentar_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        intentar_handler(update, context)

        update.message.reply_audio.assert_called_once()

    @override_settings(CHAT_ID=1)
    @patch("meals.decorators.random.randint", side_effect=[51])
    def test_intentar_handler_random_51(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        intentar_handler(update, context)

        update.message.reply_audio.assert_not_called()
