from meals.exceptions import IncompleteMeal, InvalidDay
from meals.handlers.utils import DAYS


def parse_add_meal_args(args):
    message = " ".join(args)

    meals = message.split(",")
    parsed_meals = []
    for meal in meals:
        meal = meal.strip()
        owner, *meal_elements = meal.split(" ")
        if not meal_elements:
            raise IncompleteMeal(meal)

        parsed_meals.append((owner, " ".join(meal_elements)))

    return parsed_meals


def parse_weekday_name(name):
    parsed = name.lower()
    if parsed not in DAYS:
        raise InvalidDay()
    return parsed
