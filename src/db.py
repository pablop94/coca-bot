import json
import os
import redis


LIST_KEY = "meals"
DB = redis.from_url(os.environ.get("REDIS_URL"))

print(str(DB))

def push(item):
  DB.rpush(LIST_KEY, json.dumps(item))

def pop():
  return json.loads(DB.lpop(LIST_KEY))
