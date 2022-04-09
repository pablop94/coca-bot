import logging
from datetime import timedelta
from meals.decorators import chat_id_required, meal_id_required
from meals.exceptions import IncompleteMeal
from meals.graphs import send_history_chart
from meals.handlers.utils import get_next_meal_date
from meals.models import Participant
from meals.formatters import format_name, format_meal_with_date
from meals.views import (
    add_meal,
    history,
    add_skip,
    get_next_meals,
    delete_meal,
    resolve_meal,
    get_previous_meals,
)


logger = logging.getLogger(__name__)


def parse_add_meal_args(args):
    message = " ".join(args)

    meals = message.split(",")
    parsed_meals = []
    for meal in meals:
        meal = meal.strip()
        owner, *meal_elements = meal.split(" ")
        if not meal_elements:
            raise IncompleteMeal(meal)

        parsed_meals.append((owner, " ".join(meal_elements)))

    return parsed_meals


@chat_id_required()
def add_meal_handler(update, context):
    try:
        meals_to_create = parse_add_meal_args(context.args)
    except IncompleteMeal:
        logger.info("Recibido agregar con parámetros incompletos.")
        update.message.reply_text(
            "Para que pueda agregar necesito que me pases un nombre y una comida\\."
        )
    else:
        logger.info("Agregando recordatorio de comida.")
        try:
            meal_obj = add_meal(meals_to_create)

            if len(meals_to_create) == 1:
                message = f"Ahí agregué la comida: {meal_obj.mealitem_set.first()}"
            else:
                message = "Ahí agregué la comida:"
                for meal_item in meal_obj.mealitem_set.all():
                    message += f"\n\\- {meal_item}"

            update.message.reply_text(
                message,
            )
        except Participant.DoesNotExist:
            valid_names = Participant.objects.all().values_list("name", flat=True)
            valid_names_joined = ""
            for valid_name in valid_names:
                valid_names_joined += f"\n\\- {valid_name}"
            update.message.reply_text(
                f"Hay usuarios inválidos, los válidos son:{valid_names_joined}"
            )


@chat_id_required(read_only=True)
def history_handler(update, context):
    logger.info("Enviando historial de comidas.")
    body, graph = get_history("El historial es:")

    update.message.reply_text(body)

    send_history_chart(graph, update.message.reply_photo)


def get_history(header):
    participants = history()
    graph_data = {"names": [], "values": [], "total": 0}
    body = ""
    if len(participants) > 0:
        body = f"{header} \n"
        for participant in participants:
            graph_data["names"].append(participant.name)
            graph_data["values"].append(participant.total_meals)
            graph_data["total"] += participant.total_meals

            body += f"\n\\- {format_name(participant.name)} compró para `{participant.total_meals}` comida{'s' if participant.total_meals > 1 else ''}\\."

    return body, graph_data


@chat_id_required()
def skip_handler(update, context):
    add_skip()
    logger.info("Agregando skip.")

    update.message.reply_text("Perfecto, me salteo una comida\\.")


@chat_id_required(read_only=True)
def next_meals_handler(update, context):
    meals = get_next_meals()

    if meals:
        next_date = get_next_meal_date()
        logger.info("Enviando proximas comidas.")
        message = "*Las próximas comidas son:*"
        for meal in meals:
            message += format_meal_with_date(next_date, meal)

            for meal_item in meal.mealitem_set.all():
                message += f"\n\t\\- {meal_item}"

            next_date += timedelta(weeks=1)
        update.message.reply_text(message)
    else:
        logger.info("Enviando ausencia de próximas comidas.")
        update.message.reply_text("No hay próximas comidas\\.")


@chat_id_required(read_only=True)
def previous_meals_handler(update, context):
    meals = get_previous_meals(5)

    if meals:
        logger.info("Enviando últimas 5 comidas.")
        message = "*Las últimas 5 comidas fueron:*"
        for meal in meals:
            message += format_meal_with_date(meal.done_at, meal)

            for meal_item in meal.mealitem_set.all():
                message += f"\n\t\\- {meal_item}"

        update.message.reply_text(message)
    else:
        logger.info("Enviando ausencia de últimas comidas.")
        update.message.reply_text("No hay últimas comidas\\.")


@chat_id_required()
@meal_id_required(
    action_name="borrar",
)
def delete_meal_handler(update, meal_id):
    delete_meal(meal_id)
    logger.info("Borrando comida.")
    update.message.reply_text(
        f"Borré la comida {meal_id}\\.",
    )


@chat_id_required()
@meal_id_required(
    action_name="resolver",
)
def resolve_meal_handler(update, meal_id):
    meal = resolve_meal(meal_id)
    logger.info("Resolviendo comida.")
    update.message.reply_text(
        f"Resolví la comida {meal.id}\\.",
    )


COMMANDS_ARGS = [
    ("agregar", add_meal_handler),
    ("historial", history_handler),
    ("saltear", skip_handler),
    ("proximas", next_meals_handler),
    ("borrar", delete_meal_handler),
    ("resolver", resolve_meal_handler),
    ("ultimas", previous_meals_handler),
]
