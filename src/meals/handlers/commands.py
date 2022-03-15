import logging

from telegram.ext import CommandHandler
from telegram.ext.filters import Filters

from meals.decorators import chat_id_required
from meals.graphs import send_history_chart
from meals.models import Meal
from meals.utils import format_meal, format_name
from meals.views import (
    add_meal,
    history,
    add_skip,
    get_next_meals,
    delete_meal,
    resolve_meal,
)


logger = logging.getLogger(__name__)


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
            f"Ahí le agregué la comida {format_meal(meal)} a {format_name(name)}\\.",
        )


@chat_id_required
def history_handler(update, context):
    logger.info("Enviando historial de comidas.")
    body, graph = get_history("El historial es:")

    update.message.reply_text(body)

    send_history_chart(graph, update.message.reply_photo)


def get_history(header):
    participants = history()
    graph = {"names": [], "values": [], "total": 0}
    body = ""
    if len(participants) > 0:
        body = f"{header} \n"
        for participant in participants:
            graph["names"].append(participant.name)
            graph["values"].append(participant.total_meals)
            graph["total"] += participant.total_meals

            body += f"\n\\- {format_name(participant.name)} compró para `{participant.total_meals}` comida{'s' if participant.total_meals > 1 else ''}\\."

    return body, graph


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
        for name, meal, pk in meals:
            message += f"\\- {format_meal(meal)} a cargo de {format_name(name)} \\(id: {pk}\\)\\.\n"

        update.message.reply_text(message)
    else:
        logger.info("Enviando ausencia de próximas comidas.")
        update.message.reply_text("No hay próximas comidas\\.")


@chat_id_required
def delete_meal_handler(update, context):
    try:
        if _is_valid_as_id(context.args):
            name, meal = delete_meal(context.args[0])
            logger.info("Borrando comida.")
            update.message.reply_text(
                f"Borré la comida {format_meal(meal)} a cargo de {format_name(name)}\\.",
            )
        else:
            logger.info("Recibido borrar sin parametro o con parametro invalido.")
            update.message.reply_text(
                "Para borrar necesito un id\\. Podes ver el id usando \\/proximas\\."
            )
    except Meal.DoesNotExist:
        logger.info("Se quiso borrar una comida inexistente.")
        update.message.reply_text(
            f"Nada que borrar, no hay comida con id {context.args[0]}\\."
        )


@chat_id_required
def resolve_meal_handler(update, context):
    try:
        if _is_valid_as_id(context.args):
            name, meal = resolve_meal(context.args[0])
            logger.info("Resolviendo comida.")
            update.message.reply_text(
                f"Resolví la comida {format_meal(meal)} a cargo de {format_name(name)}\\.",
            )
        else:
            logger.info("Recibido borrar sin parametro o con parametro invalido.")
            update.message.reply_text(
                "Para borrar necesito un id\\. Podes ver el id usando \\/proximas\\."
            )
    except Meal.DoesNotExist:
        logger.info("Se quiso resolver una comida inexistente.")
        update.message.reply_text(
            f"Nada que resolver, no hay comida con id {context.args[0]}\\."
        )


def _is_valid_as_id(args):
    try:
        if len(args) > 0:
            int(args[0])
            return True
        else:
            return False
    except ValueError:
        return False


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
    ("resolver", resolve_meal_handler),
]

COMMANDS = [commandHandler(*cargs) for cargs in COMMANDS_ARGS]
