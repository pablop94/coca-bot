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
    error_handler,
)
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters

if __name__ == "__main__":
    updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"))

    hour = int(os.environ.get("REMINDER_HOUR_UTC"))
    days = tuple(int(e) for e in os.environ.get("REMINDER_DAYS").split(","))
    updater.job_queue.run_daily(send_reminder, time=datetime.time(hour=hour), days=days)

    updater.dispatcher.add_handler(
        CommandHandler("agregar", add_meal_handler, Filters.command)
    )
    updater.dispatcher.add_handler(
        CommandHandler("historial", history_handler, Filters.command)
    )
    updater.dispatcher.add_handler(
        CommandHandler("saltear", skip_handler, Filters.command)
    )

    updater.dispatcher.add_handler(
        MessageHandler(
            Filters.regex(re.compile(r"\brica", re.IGNORECASE)) & ~Filters.command,
            rica_handler,
        )
    )

    updater.dispatcher.add_handler(
        MessageHandler(
            Filters.regex(re.compile(r"\b(comprar|pegar)\b", re.IGNORECASE))
            & ~Filters.command,
            pegar_handler,
        )
    )

    updater.dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
