from datetime import timedelta
from django.utils import timezone
from django.conf import settings


def get_next_meal_date():
    now = timezone.now()
    today = now.weekday()
    meal_day = settings.REMINDER_DAY + 1
    if today > meal_day:
        days_offset = 7 - (today - meal_day)
    else:
        days_offset = meal_day - today
    return now + timedelta(days=days_offset)
