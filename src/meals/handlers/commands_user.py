import logging
from datetime import timedelta
from meals.decorators import chat_id_required, meal_id_required
from meals.exceptions import IncompleteMeal, InvalidDay, NoDayReceived
from meals.graphs import send_history_chart
from meals.handlers.utils import get_next_meal_date, get_day_from_name
from meals.models import Participant, CocaSettings
from meals.formatters import format_name, format_meal_with_date
from meals.parsers import parse_add_meal_args, parse_weekday_name
from meals.views import (
    add_meal,
    history,
    add_skip,
    get_next_meals,
    delete_meal,
    copy_meal,
    resolve_meal,
    get_previous_meals,
)


logger = logging.getLogger(__name__)


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

            send_meal_created_message(meal_obj, update)
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
        reminder_day = CocaSettings.instance().reminder_day
        next_date = get_next_meal_date(reminder_day)
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
            message += format_meal_with_date(meal.done_at + timedelta(days=1), meal)

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


@chat_id_required()
@meal_id_required(
    action_name="copiar",
)
def copy_meal_handler(update, meal_id):
    meal = copy_meal(meal_id)
    logger.info("Copiando comida.")
    send_meal_created_message(meal, update)


def send_meal_created_message(meal_obj, update):
    message = "Ahí agregué la comida:"
    for meal_item in meal_obj.mealitem_set.all():
        message += f"\n\\- {meal_item}"

    update.message.reply_text(
        message,
    )


@chat_id_required()
def change_reminder_handler(update, context):
    setting = CocaSettings.instance()
    try:
        day_name = parse_weekday_name(context.args)
        setting.reminder_day = get_day_from_name(day_name)

        setting.save()

        update.message.reply_text(
            f"Se actualizó el día del recordatorio al día {day_name}\\."
        )

    except NoDayReceived:
        update.message.reply_text(
            "Necesito un día para asignar el recordatorio: lunes por ejemplo\\."
        )
    except InvalidDay:
        invalid_day = context.args[0]
        update.message.reply_text(f"{invalid_day} no es un día válido\\.")


COMMANDS_ARGS = [
    ("agregar", add_meal_handler),
    ("historial", history_handler),
    ("saltear", skip_handler),
    ("proximas", next_meals_handler),
    ("borrar", delete_meal_handler),
    ("copiar", copy_meal_handler),
    ("resolver", resolve_meal_handler),
    ("ultimas", previous_meals_handler),
    ("recordatorio", change_reminder_handler),
]
