import json
import os
import redis

from exceptions import NoMealConfigured

LIST_KEY = "meals"
DB = redis.from_url(os.environ.get("REDIS_URL"))

def push(item):
  DB.rpush(LIST_KEY, json.dumps(item))

def pop():
  meal = DB.lpop(LIST_KEY)
  if meal is None:
    raise NoMealConfigured()
  return json.loads(meal)
