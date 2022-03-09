import os
import random
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def get_handler_name(name):
    parts = name.split("_")
    return "_".join(parts[: len(parts) - 1])


def chat_id_required(fn):
    fnname = get_handler_name(fn.__name__)

    def inner(update, context):
        if update.message.chat.id == int(os.environ.get("CHAT_ID")):
            fn(update, context)
        else:
            logger.warning(
                f"Recibido <{fnname}> desde un chat no configurado: {update.message.chat.id}."
            )
            update.message.reply_photo(
                "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
            )

    return inner


def random_run(fn):
    def inner(*args, **kwargs):
        if random.randint(1, 100) <= settings.RANDOM_RUN_PROBABILITY:
            fn(*args, **kwargs)

    return inner
