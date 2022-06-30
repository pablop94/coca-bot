import random
import logging

from django.conf import settings

from meals.models import Meal, CocaSettings


logger = logging.getLogger(__name__)


def get_handler_name(name):
    parts = name.split("_")
    return "_".join(parts[: len(parts) - 1])


def chat_id_required(allow_admin_run=False, allow_user_run=True):
    """
    Marca una función como que requiere que el chat origen sea CHAT_ID.
    :param bool allow_admin_run: Especifica si el comando se puede correr desde DEVELOPER_CHAT_ID.
    """

    def decorator(fn):
        fnname = get_handler_name(fn.__name__)

        def inner(update, context):
            if (allow_user_run and update.message.chat.id == settings.CHAT_ID) or (
                allow_admin_run and update.message.chat.id == settings.DEVELOPER_CHAT_ID
            ):
                fn(update, context)
            else:
                logger.warning(
                    f"Recibido <{fnname}> desde un chat no configurado: {update.message.chat.id}."
                )
                update.message.reply_photo(
                    "https://pbs.twimg.com/media/E8ozthsWQAMproa.jpg"
                )

        return inner

    return decorator


def random_run(fn):
    def inner(*args, **kwargs):
        if random.randint(1, 100) <= CocaSettings.instance().random_run_probability:
            fn(*args, **kwargs)

    return inner


def meal_id_required(action_name=None):
    def decorator(fn):
        def inner(update, context):
            try:
                if _is_valid_as_id(context.args):
                    meal_id = context.args[0]
                    fn(update, meal_id)
                else:
                    logger.info(
                        f"Recibido {action_name} sin parametro o con parametro invalido."
                    )
                    update.message.reply_text(
                        f"Para {action_name} necesito un id\\. Podes ver el id usando \\/proximas\\."
                    )
            except Meal.DoesNotExist:
                logger.info(f"Se quiso {action_name} una comida inexistente.")
                update.message.reply_text(
                    f"Nada que {action_name}, no hay comida con id {meal_id}\\."
                )

        return inner

    return decorator


def _is_valid_as_id(args):
    try:
        if len(args) > 0:
            int(args[0])
            return True
        else:
            return False
    except ValueError:
        return False
