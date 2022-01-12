import os

from telegram import Bot, Update
from telegram.ext import Dispatcher
from src.coca import add_handlers
from src.logger import logger


def new_update(request):
    if request.method == "POST":
        logger.info("POST request received")
        bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
        dispatcher = Dispatcher(bot, None, workers=0)
        update = Update.de_json(request.get_json(force=True), bot)

        add_handlers(dispatcher)

        dispatcher.process_update(update)
    return "ok"
