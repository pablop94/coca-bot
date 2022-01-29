import json
from src.db import push, lpop, llen, get, rpop
from src.exceptions import NoMealConfigured

MEALS_KEY = "meals"
HISTORY_KEY = "history"
SKIP_KEY = "skip"


def add_meal(user, meal):
    push(MEALS_KEY, json.dumps({"name": user, "meal": meal}))


def get_next_meal():
    item = lpop(MEALS_KEY)
    if item is None:
        raise NoMealConfigured()

    meal = json.loads(item)
    return meal["name"], meal["meal"], _remaining_meals()


def get_last_meal():
    item = rpop(MEALS_KEY)
    if item is None:
        raise NoMealConfigured()

    meal = json.loads(item)
    return meal["name"], meal["meal"]


def history():
    return get(HISTORY_KEY)


def add_history(name):
    push(HISTORY_KEY, name)


def _remaining_meals():
    return llen(MEALS_KEY)


def get_skip():
    return lpop(SKIP_KEY)


def add_skip():
    push(SKIP_KEY, "skip")


def get_next_meals():
    result = []
    for item in get(MEALS_KEY):
        name, meal = json.loads(item).values()
        result.append((name, meal))

    return result
