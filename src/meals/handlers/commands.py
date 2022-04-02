from telegram.ext import CommandHandler
from telegram.ext.filters import Filters

from meals.handlers.commands_user import COMMANDS_ARGS as USER_COMMANDS_ARGS
from meals.handlers.commands_admin import COMMANDS_ARGS as ADMIN_COMMANDS_ARGS


def commandHandler(name, handler):
    return CommandHandler(
        name,
        handler,
        Filters.command & ~Filters.update.edited_message,
    )


COMMANDS_ARGS = USER_COMMANDS_ARGS + ADMIN_COMMANDS_ARGS

COMMANDS = [commandHandler(*cargs) for cargs in COMMANDS_ARGS]
