import random
import re
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

from src.logger import logger


def rica_handler(update, context):
    _send_audio(update, "rica.mp3", "rica, rica... amarga")


def pegar_handler(update, context):
    _send_audio(update, "pegar.mp3", "pegar falopa")


def chocolate_handler(update, context):
    _send_audio(update, "chocolate.mp3", "chocolate")


def intentar_handler(update, context):
    _send_audio(update, "intentar.mp3", "intentar")


def _send_audio(update, audio_name, title):
    if random.randint(1, 100) < 25:
        logger.info(f"Enviando audio {audio_name}")
        with open(f"media/{audio_name}", "rb") as audio:
            update.message.reply_audio(audio=audio, title=title)


def regexMessageHandler(regex, handler):
    return MessageHandler(
        Filters.regex(re.compile(regex, re.IGNORECASE)) & ~Filters.command,
        handler,
    )


REACTIONS_ARGS = [
    (r"\brica", rica_handler),
    (r"\b(comprar|pegar|compra)\b", pegar_handler),
    (r"\bchocolate", chocolate_handler),
    (r"\bintentar", intentar_handler),
]

REACTIONS = [regexMessageHandler(*rargs) for rargs in REACTIONS_ARGS]
