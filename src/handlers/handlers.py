import html
import json
import os
import traceback

from src.exceptions import NoMealConfigured
from src.logger import logger
from src.meals import get_next_meal, add_history, get_skip
from telegram import ParseMode, Update


def send_reminder(context):
    send_reminder_from_bot(context.bot)


def send_reminder_from_bot(bot):
    if not get_skip():
        try:
            name, meal, remaining = get_next_meal()
            add_history(name)
            logger.info("Enviando recordatorio de comida.")
            bot.send_message(
                os.environ.get("CHAT_ID"),
                f"Hola `{name}` te toca comprar los ingredientes para hacer `{meal}`",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            if remaining == 0:
                bot.send_message(
                    os.environ.get("CHAT_ID"),
                    "Además les informo que no hay más comidas configuradas, ponganse a pensar",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
        except NoMealConfigured:
            logger.info("Comida sin configurar.")
            bot.send_message(
                os.environ.get("CHAT_ID"),
                "Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas.",
            )
    else:
        logger.info("Salteando recordatorio debido a un skip.")


def error_handler(update, context):
    logger.error(msg="Error procesando un update:", exc_info=context.error)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    message = (
        f"Hubo un error al procesar un update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    context.bot.send_message(
        os.environ.get("DEVELOPER_CHAT_ID"), text=message, parse_mode=ParseMode.HTML
    )
