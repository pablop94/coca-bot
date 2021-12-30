import html
import json
import os
import traceback

from src.exceptions import NoMealConfigured
from src.logger import logger
from src.meals import add_meal, get_next_meal, history, add_history, get_skip, add_skip
from telegram import ParseMode, Update


def get_handler_name(name):
  parts = name.split('_')
  return '_'.join(parts[:len(parts)-1])


def chat_id_required(fn):
  fnname = get_handler_name(fn.__name__)

  def inner(update, context):
    if update.message.chat.id == int(os.environ.get("CHAT_ID")):
      fn(update, context) 
    else: 
      logger.warning(f"Recibido <{fnname}> desde un chat no configurado: {update.message.chat.id}.")
      update.message.reply_photo('https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg')

  return inner


def send_reminder(context):
  if not get_skip():
    try:
      name, meal, remaining = get_next_meal()
      add_history(name)
      logger.info("Enviando recordatorio de comida.")
      context.bot.send_message(os.environ.get(
        "CHAT_ID"), f"Hola `{name}` te toca comprar los ingredientes para hacer `{meal}`", parse_mode=ParseMode.MARKDOWN_V2)
      if remaining == 0:
        context.bot.send_message(os.environ.get(
          "CHAT_ID"), f"Además les informo que no hay más comidas configuradas, ponganse a pensar", parse_mode=ParseMode.MARKDOWN_V2)
    except NoMealConfigured:
      logger.info("Comida sin configurar.")
      context.bot.send_message(os.environ.get(
        "CHAT_ID"), f"Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas.")
  else: 
    logger.info("Salteando recordatorio debido a un skip.")

@chat_id_required
def add_meal_handler(update, context):
  if len(context.args) < 2:
    logger.info("Recibido agregar con parámetros incompletos.")
    update.message.reply_text(
      "Para que pueda agregar necesito que me pases un nombre y una comida")
  else:
      logger.info("Agregando recordatorio de comida.")
      meal = ' '.join(context.args[1:])
      name = context.args[0]
      add_meal(name, meal)
      update.message.reply_text(
        f"Ahí le agregué la comida `{meal}` a `{name}`", parse_mode=ParseMode.MARKDOWN_V2)


@chat_id_required
def history_handler(update, context):
  names = history()
  aggregation = dict()
  for bname in names:
    name = bname if not type(bname) is bytes else bname.decode("utf-8")
    if name not in aggregation:
      aggregation[name] = 0
    aggregation[name] += 1

  if len(names)>0:
    body = "El historial es\n"
    for name in aggregation.keys():
      body += f"\n{name}: {aggregation[name]}"
  
    logger.info("Enviando historial de comidas.")

  update.message.reply_text(body, parse_mode=ParseMode.MARKDOWN_V2)

@chat_id_required
def skip_handler(update, context):
  add_skip()

  update.message.reply_text("Perfecto, me salteo una comida", parse_mode=ParseMode.MARKDOWN_V2)

def error_handler(update, context):
  logger.error(msg="Error procesando un update:", exc_info=context.error)
  update_str = update.to_dict() if isinstance(update, Update) else str(update)
  tb_list = traceback.format_exception(
      None, context.error, context.error.__traceback__)
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
  context.bot.send_message(os.environ.get(
    "DEVELOPER_CHAT_ID"), text=message, parse_mode=ParseMode.HTML)
