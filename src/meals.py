import json
from src.db import push, pop, llen, get
from src.exceptions import NoMealConfigured

MEALS_KEY = "meals"
HISTORY_KEY = "history"
SKIP_KEY = "skip"


def add_meal(user, meal):
    push(MEALS_KEY, json.dumps({"name": user, "meal": meal}))


def get_next_meal():
    item = pop(MEALS_KEY)
    if item is None:
        raise NoMealConfigured()

    meal = json.loads(item)
    return meal["name"], meal["meal"], _remaining_meals()


def history():
    return get(HISTORY_KEY)


def add_history(name):
    push(HISTORY_KEY, name)


def _remaining_meals():
    return llen(MEALS_KEY)


def get_skip():
    return pop(SKIP_KEY)


def add_skip():
    push(SKIP_KEY, "skip")
