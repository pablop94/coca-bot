import datetime
import os
import re

from src.handlers import (
    send_reminder,
    add_meal_handler,
    history_handler,
    skip_handler,
    rica_handler,
    pegar_handler,
    chocolate_handler,
    intentar_handler,
    error_handler,
)
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters


def regexMessageHandler(regex, handler):
    return MessageHandler(
        Filters.regex(re.compile(regex, re.IGNORECASE)) & ~Filters.command,
        handler,
    )


def commandHandler(name, handler):
    return CommandHandler(
        name,
        handler,
        Filters.command & ~Filters.update.edited_message,
    )


COMMANDS = [
    ("agregar", add_meal_handler),
    ("historial", history_handler),
    ("saltear", skip_handler),
]

REACTIONS = [
    (r"\brica", rica_handler),
    (r"\b(comprar|pegar|compra)\b", pegar_handler),
    (r"\bchocolate", chocolate_handler),
    (r"\bintentar", intentar_handler),
]


def add_handlers(dispatcher):
    for name, handler in COMMANDS:
        dispatcher.add_handler(commandHandler(name, handler))

    for regex, handler in REACTIONS:
        dispatcher.add_handler(regexMessageHandler(regex, handler))


def start_bot():
    updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"))

    hour = int(os.environ.get("REMINDER_HOUR_UTC"))
    days = tuple(int(e) for e in os.environ.get("REMINDER_DAYS").split(","))
    updater.job_queue.run_daily(send_reminder, time=datetime.time(hour=hour), days=days)

    add_handlers(updater.dispatcher)

    updater.dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_bot()
