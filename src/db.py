import os
import redis

DB = redis.from_url(os.environ.get("REDIS_URL"))

def push(key, item):
  DB.rpush(key, item)

def pop(key):
  return DB.lpop(key)

def llen(key):
  return DB.llen(key)

def get(key):
  return DB.lrange(key, 0, -1)