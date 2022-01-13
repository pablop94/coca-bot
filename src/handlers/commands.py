from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext.filters import Filters

from src.decorators import chat_id_required
from src.logger import logger
from src.meals import add_meal, history, add_skip


@chat_id_required
def add_meal_handler(update, context):
    if len(context.args) < 2:
        logger.info("Recibido agregar con parámetros incompletos.")
        update.message.reply_text(
            "Para que pueda agregar necesito que me pases un nombre y una comida"
        )
    else:
        logger.info("Agregando recordatorio de comida.")
        meal = " ".join(context.args[1:])
        name = context.args[0]
        add_meal(name, meal)
        update.message.reply_text(
            f"Ahí le agregué la comida `{meal}` a `{name}`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


@chat_id_required
def history_handler(update, context):
    names = history()
    aggregation = dict()
    for bname in names:
        name = bname if not type(bname) is bytes else bname.decode("utf-8")
        if name not in aggregation:
            aggregation[name] = 0
        aggregation[name] += 1

    if len(names) > 0:
        body = "El historial es\n"
        for name in aggregation.keys():
            body += f"\n{name}: {aggregation[name]}"

        logger.info("Enviando historial de comidas.")

        update.message.reply_text(body, parse_mode=ParseMode.MARKDOWN_V2)


@chat_id_required
def skip_handler(update, context):
    add_skip()

    update.message.reply_text(
        "Perfecto, me salteo una comida", parse_mode=ParseMode.MARKDOWN_V2
    )


def commandHandler(name, handler):
    return CommandHandler(
        name,
        handler,
        Filters.command & ~Filters.update.edited_message,
    )


COMMANDS_ARGS = [
    ("agregar", add_meal_handler),
    ("historial", history_handler),
    ("saltear", skip_handler),
]

COMMANDS = [commandHandler(*cargs) for cargs in COMMANDS_ARGS]
