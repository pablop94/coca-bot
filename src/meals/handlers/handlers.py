import html
import json
import traceback
import logging
from django.conf import settings
from meals.decorators import random_run
from meals.exceptions import NoMealConfigured
from meals.graphs import send_history_chart
from meals.handlers.commands_user import get_history
from meals.formatters import format_meal, format_name
from meals.views import get_next_meal, get_skip, get_todays_birthdays
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def send_reminder(context):
    send_reminder_from_bot(context.bot)


def send_reminder_from_bot(bot):
    if not get_skip():
        try:
            meal, remaining = get_next_meal()
            logger.info("Enviando recordatorio de comida.")
            message = "Hola\\!"
            for meal_item in meal.mealitem_set.all():
                message += f"\n\\- {format_name(meal_item.owner.name)} te toca comprar los ingredientes para hacer {format_meal(meal_item.description)}\\."
            bot.send_message(
                settings.CHAT_ID,
                message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info(f"remaining {remaining}")
            if remaining == 0:
                bot.send_message(
                    settings.CHAT_ID,
                    "Además les informo que no hay más comidas configuradas, ponganse a pensar\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
        except NoMealConfigured:
            logger.info("Comida sin configurar.")
            bot.send_message(
                settings.CHAT_ID,
                "Hola, no hay una comida configurada para mañana, si quieren cenar rico ponganse las pilas\\.",
            )
        except Exception as e:
            meal.done = False
            meal.done_at = None
            meal.save()
            raise e
    else:
        logger.info("Salteando recordatorio debido a un skip.")


def send_history_resume(context):
    body, graph = get_history("Hola, les dejo el resumen del histórico de compras:")

    context.bot.send_message(settings.CHAT_ID, body)

    send_history_chart(
        graph,
        lambda image, **kwargs: context.bot.send_photo(
            settings.CHAT_ID, image, **kwargs
        ),
    )


def error_handler(update, context):
    logger.error(msg="Error procesando un update:", exc_info=context.error)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    message = (
        f"Hubo un error al procesar un update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    context.bot.send_message(
        settings.DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


@random_run
def reply_to_coca_handler(update: Update, context: CallbackContext):
    if update.message.reply_to_message.from_user.id == int(
        settings.TELEGRAM_TOKEN.split(":")[0]
    ):
        update.message.reply_text("Soy una entidad virtual, no me contestes\\.")


def send_birthdays_handler(context: CallbackContext):
    today_birthdays = get_todays_birthdays()

    for birthday in today_birthdays:
        context.bot.send_message(
            settings.CHAT_ID,
            f"Feliz cumple {birthday.name}\\!\\! La próxima tenes que llevar flan\\.",
        )
