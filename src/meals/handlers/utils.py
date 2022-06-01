from datetime import timedelta
from django.utils import timezone


def get_next_meal_date(reminder_day):
    now = timezone.now()
    today = now.weekday()
    meal_day = reminder_day + 1
    if today > meal_day:
        days_offset = 7 - (today - meal_day)
    else:
        days_offset = meal_day - today
    return now + timedelta(days=days_offset)
