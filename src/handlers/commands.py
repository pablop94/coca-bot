from telegram.ext import CommandHandler
from telegram.ext.filters import Filters

from src.decorators import chat_id_required
from src.logger import logger
from src.exceptions import NoMealConfigured
from src.meals import (
    add_meal,
    history,
    add_skip,
    get_next_meals,
    get_next_meal,
    get_last_meal,
)


@chat_id_required
def add_meal_handler(update, context):
    if len(context.args) < 2:
        logger.info("Recibido agregar con parámetros incompletos.")
        update.message.reply_text(
            "Para que pueda agregar necesito que me pases un nombre y una comida\\."
        )
    else:
        logger.info("Agregando recordatorio de comida.")
        meal = " ".join(context.args[1:])
        name = context.args[0]
        add_meal(name, meal)
        update.message.reply_text(
            f"Ahí le agregué la comida `{meal}` a *{name}*\\.",
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

        update.message.reply_text(body)


@chat_id_required
def skip_handler(update, context):
    add_skip()
    logger.info("Agregando skip.")

    update.message.reply_text("Perfecto, me salteo una comida\\.")


@chat_id_required
def next_meals_handler(update, context):
    meals = get_next_meals()

    if meals:
        logger.info("Enviando proximas comidas.")
        message = "Las próximas comidas son:\n"
        for name, meal in meals:
            message += f"\\- `{meal}` a cargo de *{name}*\\.\n"

        update.message.reply_text(message)
    else:
        logger.info("Enviando ausencia de próximas comidas.")
        update.message.reply_text("No hay próximas comidas\\.")


@chat_id_required
def delete_meal_handler(update, context):
    try:
        retrieve_func = (
            get_last_meal if _is_last_meal_deletion(context.args) else get_next_meal
        )

        name, meal, *_ = retrieve_func()
        logger.info("Borrando comida.")
        update.message.reply_text(
            f"Borré la comida `{meal}` a cargo de *{name}*\\.",
        )

    except NoMealConfigured:
        logger.info("No hay comidas para borrar.")
        update.message.reply_text("Nada que borrar, no hay comidas\\.")


def _is_last_meal_deletion(args):
    return len(args) > 0 and args[0] == "ultima"


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
    ("proximas", next_meals_handler),
    ("borrar", delete_meal_handler),
]

COMMANDS = [commandHandler(*cargs) for cargs in COMMANDS_ARGS]
