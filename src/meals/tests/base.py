from unittest.mock import MagicMock


class MockChat:
    def __init__(self):
        self.id = 1


class MockMessage:
    def __init__(self):
        self.chat = MockChat()
        self.reply_text = MagicMock()
        self.reply_photo = MagicMock()
        self.reply_audio = MagicMock()


def get_mock_update(args=[]):
    class MockUpdate:
        def __init__(self):
            self.message = MockMessage()
            self.args = args

    return MockUpdate()


def get_mock_context(args=[]):
    class MockContext:
        def __init__(self):
            self.bot = MagicMock()
            self.args = args
            self.bot.send_message = MagicMock()
            self.bot.send_photo = MagicMock()
            self.job_queue = MagicMock()

    return MockContext()
