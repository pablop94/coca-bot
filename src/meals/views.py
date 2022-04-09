import random
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


def get_previous_meals(limit):
    return Meal.objects.filter(done=True).order_by("-id")[:limit]


def resolve_meal(meal_id):
    meal = Meal.objects.get(id=meal_id)
    meal.mark_as_done()
    meal.save()

    return meal


def copy_meal(meal_id):
    new_meal = Meal.objects.create()

    meal = Meal.objects.get(id=meal_id)
    possible_owners = set(
        Participant.objects.exclude(
            id__in=meal.mealitem_set.values("owner_id")
        ).values_list("id", flat=True)
    )

    new_items = []
    for meal_item in meal.mealitem_set.all():
        if possible_owners:
            owner = random.choice(list(possible_owners))
            possible_owners.remove(owner)
        else:
            owner = meal_item.owner_id

        new_items.append(
            MealItem(meal=new_meal, owner_id=owner, description=meal_item.description)
        )

    MealItem.objects.bulk_create(new_items)

    return new_meal
