import json
from src.db import push, pop, llen
from src.exceptions import NoMealConfigured

MEALS_KEY = "meals"

def add_meal(user, meal):
  push(MEALS_KEY, json.dumps({"name": user, "meal": meal}))

def get_next_meal():
  item = pop(MEALS_KEY)
  if item is None:
    raise NoMealConfigured()

  meal = json.loads(item)
  return meal['name'], meal['meal'], remaining_meals()

def remaining_meals():
  return llen(MEALS_KEY)