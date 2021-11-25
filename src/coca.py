import datetime
import html
import json
import logging
import os
import traceback

from exceptions import NoMealConfigured
from meals import add, get_next_meal
from telegram import ParseMode, Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram.ext.filters import Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def send_reminder(context: CallbackContext):
  try:
    name, meal = get_next_meal()
    logger.info("Enviando recordatorio de comida.")
    context.bot.send_message(os.environ.get(
        "CHAT_ID"), f"Hola `{name}` hoy te toca comprar los ingredientes para hacer `{meal}`")
  except NoMealConfigured:
    logger.info("Comida sin configurar.")
    context.bot.send_message(os.environ.get(
        "CHAT_ID"), f"Hola, no hay una comida configurada para hoy, si quieren cenar rico ponganse las pilas.")


def add_meal(update, context):
  if len(context.args) < 2: 
    logger.info("Recibido agregar con parámetros incompletos.")
    update.message.reply_text("Para que pueda agregar necesito que me pases un nombre y una comida")
  else:
    logger.info("Agregando recordatorio de comida.")
    meal = ' '.join(context.args[1:])
    name = context.args[0]
    add(name, meal)
    update.message.reply_text(
        f"Ahí le agregué la comida `{meal}` a `{name}`", parse_mode=ParseMode.MARKDOWN_V2)

def error_handler(update, context):
  logger.error(msg="Error manejando un update:", exc_info=context.error)
  update_str = update.to_dict() if isinstance(update, Update) else str(update)
  tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
  tb_string = ''.join(tb_list)

  message = (
      f'Hubo un error al procesar un update\n'
      f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
      '</pre>\n\n'
      f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
      f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
      f'<pre>{html.escape(tb_string)}</pre>'
  )

  # Finally, send the message
  context.bot.send_message(os.environ.get("DEVELOPER_CHAT_ID"), text=message, parse_mode=ParseMode.HTML)



updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"))
updater.job_queue.run_daily(send_reminder, time=datetime.time(
    hour=16, minute=00, second=00), days=(3,))

updater.dispatcher.add_handler(CommandHandler(
    "agregar", add_meal, Filters.command))

updater.dispatcher.add_error_handler(error_handler)

updater.start_polling()
updater.idle()
