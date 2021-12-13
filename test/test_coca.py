import json 

from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from src.handlers import send_reminder, add_meal_handler, history_handler
from src.exceptions import NoMealConfigured
from telegram import ParseMode

class MockBot:
  pass

class MockChat:
  def __init__(self):
    self.id = 1

class MockMessage:
  def __init__(self):
    self.chat = MockChat()
    self.reply_text = MagicMock()
    self.reply_photo = MagicMock()

def get_mock_context(args=[]):
  class MockContext:
    def __init__(self):
      self.bot = MockBot()
      self.args = args
      self.bot.send_message = MagicMock()

  return MockContext()
def get_mock_update(args=[]):
  class MockUpdate:
    def __init__(self):
      self.message = MockMessage()
      self.args = args

  return MockUpdate()


class CocaTest(TestCase):
  @patch.dict('os.environ', {'CHAT_ID': ''})
  @patch('src.handlers.get_next_meal', side_effect=[('test name', 'test meal', 4)])
  @patch('src.handlers.add_history')
  def test_send_reminder(self, *args):
    context = get_mock_context()
    send_reminder(context)

    context.bot.send_message.assert_called_once_with('', "Hola `test name` te toca comprar los ingredientes para hacer `test meal`", parse_mode=ParseMode().MARKDOWN_V2)
    
  @patch.dict('os.environ', {'CHAT_ID': ''})
  @patch('src.handlers.get_next_meal', side_effect=[('test name', 'test meal', 4)])
  @patch('src.handlers.add_history')
  def test_send_reminder_add_history(self, addhistoryfn, *args):
    context = get_mock_context()
    send_reminder(context)

    addhistoryfn.assert_called_once_with('test name')
    
  @patch.dict('os.environ', {'CHAT_ID': ''})
  @patch('src.handlers.get_next_meal', side_effect=[('test name', 'test meal', 0)])
  @patch('src.handlers.add_history')
  def test_send_reminder_no_more_meals(self, *args):
    context = get_mock_context()
    send_reminder(context)

    self.assertEqual(2, context.bot.send_message.call_count)
    context.bot.send_message.assert_has_calls([
      call('', "Hola `test name` te toca comprar los ingredientes para hacer `test meal`", parse_mode=ParseMode().MARKDOWN_V2),
      call('', "Además les informo que no hay más comidas configuradas, ponganse a pensar", parse_mode=ParseMode().MARKDOWN_V2)
    ])


  def no_meal_configured():
    raise NoMealConfigured()

  @patch.dict('os.environ', {'CHAT_ID': ''})
  @patch('src.handlers.get_next_meal', side_effect=no_meal_configured)
  def test_send_reminder_no_meal(self, *args):
    context = get_mock_context()
    send_reminder(context)

    context.bot.send_message.assert_called_once_with('', "Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas.")
    

  @patch.dict('os.environ', {'CHAT_ID': '1'})
  @patch('src.handlers.add_meal')
  def test_add_meal_handler(self, *args):
    context = get_mock_context(['name', 'meal'])
    update = get_mock_update()
    add_meal_handler(update, context)

    update.message.reply_text.assert_called_once_with("Ahí le agregué la comida `meal` a `name`", parse_mode=ParseMode.MARKDOWN_V2)
    
  @patch.dict('os.environ', {'CHAT_ID': '1'})
  @patch('src.handlers.get_next_meal', side_effect=no_meal_configured)
  def test_add_meal_handler_no_args(self, *args):
    context = get_mock_context()
    update = get_mock_update()
    add_meal_handler(update, context)

    update.message.reply_text.assert_called_once_with("Para que pueda agregar necesito que me pases un nombre y una comida")
    
  @patch.dict('os.environ', {'CHAT_ID': '2'})
  @patch('src.handlers.get_next_meal', side_effect=no_meal_configured)
  def test_add_meal_handler_unknown_chat(self, *args):
    context = get_mock_context([1, 2])
    update = get_mock_update()
    add_meal_handler(update, context)

    update.message.reply_photo.assert_called_once_with('https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg')
    

  @patch.dict('os.environ', {'CHAT_ID': '1'})
  @patch('src.handlers.history', side_effect=[['test1', 'test2', 'test1']])
  def test_history_handler(self, *args):
    context = get_mock_context(['name', 'meal'])
    update = get_mock_update()
    history_handler(update, context)

    update.message.reply_text.assert_called_once_with("El historial es\n\ntest1: 2\ntest2: 1", parse_mode=ParseMode.MARKDOWN_V2)
    

  @patch.dict('os.environ', {'CHAT_ID': '2'})
  @patch('src.handlers.history', side_effect=[['test1', 'test2', 'test1']])
  def test_history_handler_unknown_chat(self, *args):
    context = get_mock_context(['name', 'meal'])
    update = get_mock_update()
    history_handler(update, context)

    update.message.reply_photo.assert_called_once_with('https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg')