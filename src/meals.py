import json
from .db import push, pop
from .exceptions import NoMealConfigured


def add_meal(user, meal):
  push(json.dumps({"name": user, "meal": meal}))

def get_next_meal():
  item = pop()
  if item is None:
    raise NoMealConfigured()

  meal = json.loads(item)
  return meal['name'], meal['meal']