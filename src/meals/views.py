from django.db import transaction
from django.db.models import Count
from meals.exceptions import NoMealConfigured
from meals.models import Meal, MealItem, Participant, Skip


def add_meal(meals_to_create):
    with transaction.atomic():
        meal = Meal.objects.create()

        MealItem.objects.bulk_create(
            [
                MealItem(
                    owner=Participant.objects.get(name__iexact=owner),
                    description=description,
                    meal=meal,
                )
                for owner, description in meals_to_create
            ]
        )

        return meal


def get_next_meal():
    meal = Meal.objects.filter(done=False).first()
    if meal is None:
        raise NoMealConfigured()

    meal.mark_as_done()
    meal.save()

    return meal, _remaining_meals()


def delete_meal(meal_id):
    meal = Meal.objects.get(pk=meal_id)

    meal.delete()

    return meal


def history():
    return (
        Participant.objects.filter(mealitem__meal__done=True)
        .annotate(total_meals=Count("mealitem__meal__pk"))
        .order_by("-total_meals")
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
