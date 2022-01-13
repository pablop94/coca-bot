import datetime
import os

from src.handlers import (
    send_reminder,
    COMMANDS,
    REACTIONS,
    error_handler,
)
from telegram.ext import Updater


def add_handlers(dispatcher):
    for command in COMMANDS:
        dispatcher.add_handler(command)

    for reaction in REACTIONS:
        dispatcher.add_handler(reaction)

    dispatcher.add_error_handler(error_handler)


def start_bot():
    updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"))

    hour = int(os.environ.get("REMINDER_HOUR_UTC"))
    days = tuple(int(e) for e in os.environ.get("REMINDER_DAYS").split(","))
    updater.job_queue.run_daily(send_reminder, time=datetime.time(hour=hour), days=days)

    add_handlers(updater.dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_bot()
