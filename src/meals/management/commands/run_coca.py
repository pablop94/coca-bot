import datetime
import os
from django.conf import settings
from meals.handlers import (
    send_reminder,
    send_history_resume,
    COMMANDS,
    REACTIONS,
    error_handler,
    reply_to_coca_handler,
)
from telegram import ParseMode
from telegram.ext import Updater, MessageHandler, Defaults
from telegram.ext.filters import Filters

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        start_bot()


def add_handlers(dispatcher):
    for command in COMMANDS:
        dispatcher.add_handler(command)

    for reaction in REACTIONS:
        dispatcher.add_handler(reaction)

    dispatcher.add_handler(
        MessageHandler(Filters.reply & ~Filters.command, reply_to_coca_handler)
    )

    dispatcher.add_error_handler(error_handler)


def start_bot():
    defaults = Defaults(quote=False, parse_mode=ParseMode.MARKDOWN_V2)
    updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"), defaults=defaults)

    days = tuple(int(e) for e in os.environ.get("REMINDER_DAYS").split(","))
    hour = int(os.environ.get("REMINDER_HOUR_UTC"))
    minute = 0 if not settings.DEBUG else datetime.datetime.now().minute + 1
    updater.job_queue.run_daily(
        send_reminder,
        time=datetime.time(hour=hour, minute=minute),
        days=days,
    )

    history_day = int(os.environ.get("HISTORY_RESUME_DAY", 31))
    updater.job_queue.run_monthly(
        send_history_resume,
        when=datetime.time(hour=hour, minute=minute),
        day=history_day,
        day_is_strict=False,
    )
    add_handlers(updater.dispatcher)

    updater.start_polling()
    updater.idle()