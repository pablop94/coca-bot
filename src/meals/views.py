from meals.exceptions import NoMealConfigured
from meals.models import Meal, Participant, Skip

MEALS_KEY = "meals"
HISTORY_KEY = "history"
SKIP_KEY = "skip"


def add_meal(user, meal):
    Meal.objects.create(
        meal_owner=Participant.objects.get_or_create(name=user)[0], description=meal
    )


def get_next_meal():
    meal = Meal.objects.first()
    if meal is None:
        raise NoMealConfigured()

    meal.done = True
    meal.save()

    return meal.meal_owner.name, meal.description, _remaining_meals()


def delete_meal(id):
    meal = Meal.objects.get(pk=id)

    meal.delete()

    return meal.meal_owner.name, meal.description


def history():
    pass
    # return get(HISTORY_KEY)


def _remaining_meals():
    return Meal.objects.filter(done=False).count()


def get_skip():
    skip = Skip.objects.first()

    if skip:
        skip.delete()

    return skip


def add_skip():
    Skip.objects.create()


def get_next_meals():
    return Meal.objects.filter(done=False).values_list(
        "meal_owner__name", "description", "pk"
    )
