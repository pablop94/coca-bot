import datetime
from django.conf import settings
from meals.handlers import (
    send_reminder,
    send_history_resume,
    COMMANDS,
    REACTIONS,
    error_handler,
    reply_to_coca_handler,
    send_birthdays_handler,
)
from meals.models import CocaSettings
from telegram import ParseMode
from telegram.ext import Updater, MessageHandler, Defaults
from telegram.ext.filters import Filters

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start coca in polling mode"

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
    updater = Updater(token=settings.TELEGRAM_TOKEN, defaults=defaults)

    coca_settings = CocaSettings.instance()
    day = coca_settings.reminder_day
    hour = coca_settings.reminder_hour_utc
    minute = 0 if not settings.DEBUG else datetime.datetime.now().minute + 1
    updater.job_queue.run_daily(
        send_reminder,
        time=datetime.time(hour=hour, minute=minute),
        days=(day,),
    )

    history_day = coca_settings.history_resume_day
    updater.job_queue.run_monthly(
        send_history_resume,
        when=datetime.time(hour=hour, minute=minute),
        day=history_day,
    )

    updater.job_queue.run_daily(
        send_birthdays_handler,
        time=datetime.time(hour=hour, minute=minute),
    )

    add_handlers(updater.dispatcher)

    updater.start_polling()
    updater.idle()
