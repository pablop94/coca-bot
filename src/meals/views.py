from django.db.models import Count
from meals.exceptions import NoMealConfigured
from meals.models import Meal, Participant, Skip


def add_meal(user, meal):
    return Meal.objects.create(
        meal_owner=Participant.objects.get_or_create(
            name__iexact=user, defaults={"name": user}
        )[0],
        description=meal,
    )


def get_next_meal():
    meal = Meal.objects.filter(done=False).first()
    if meal is None:
        raise NoMealConfigured()

    meal.mark_as_done()
    meal.save()

    return meal.meal_owner.name, meal.description, _remaining_meals()


def delete_meal(meal_id):
    meal = Meal.objects.get(pk=meal_id)

    meal.delete()

    return meal


def history():
    return Participant.objects.filter(meal__done=True).annotate(
        total_meals=Count("meal__pk")
    )


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
    return Meal.objects.filter(done=False)


def resolve_meal(meal_id):
    meal = Meal.objects.get(id=meal_id)
    meal.mark_as_done()
    meal.save()

    return meal
