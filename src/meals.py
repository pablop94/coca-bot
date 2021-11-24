from db import push, pop


def add(user, meal):
  push({"name": user, "meal": meal})

def get_next_meal():
  elem = pop()
  return elem['name'], elem['meal']