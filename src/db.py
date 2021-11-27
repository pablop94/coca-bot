import os
import redis

LIST_KEY = "meals"
DB = redis.from_url(os.environ.get("REDIS_URL"))

def push(item):
  DB.rpush(LIST_KEY, item)

def pop():
  return DB.lpop(LIST_KEY)
