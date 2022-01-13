import os
from src.logger import logger


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
