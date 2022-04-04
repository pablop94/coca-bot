import re
import logging
from os import path
from pathlib import Path
from django.conf import settings
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

from meals.decorators import chat_id_required, random_run

logger = logging.getLogger(__name__)


@random_run
@chat_id_required()
def rica_handler(update, context):
    _send_audio(update, "rica.mp3", "rica, rica... amarga")


@random_run
@chat_id_required()
def pegar_handler(update, context):
    _send_audio(update, "pegar.mp3", "pegar falopa")


@random_run
@chat_id_required()
def chocolate_handler(update, context):
    _send_audio(update, "chocolate.mp3", "chocolate")


@random_run
@chat_id_required()
def intentar_handler(update, context):
    _send_audio(update, "intentar.mp3", "intentar")


def _send_audio(update, audio_name, title):
    logger.info(f"Enviando audio {audio_name}")
    with open(
        path.join(Path(settings.BASE_DIR).parent, "media", audio_name), "rb"
    ) as audio:
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
