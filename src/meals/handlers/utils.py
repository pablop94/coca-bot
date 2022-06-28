import calendar
from datetime import timedelta
from django.utils import timezone

DAYS = {
    "lunes": calendar.MONDAY,
    "martes": calendar.TUESDAY,
    "miercoles": calendar.WEDNESDAY,
    "jueves": calendar.THURSDAY,
    "viernes": calendar.FRIDAY,
    "sabado": calendar.SATURDAY,
    "domingo": calendar.SUNDAY,
}


def get_next_meal_date(reminder_day):
    now = timezone.now()
    today = now.weekday()
    meal_day = reminder_day + 1
    if today > meal_day:
        days_offset = 7 - (today - meal_day)
    else:
        days_offset = meal_day - today
    return now + timedelta(days=days_offset)


def get_day_from_name(day_name):
    return DAYS[day_name]
