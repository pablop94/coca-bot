def format_name(name):
    return f"*{name}*"


def format_meal(meal):
    return f"`{meal}`"


def format_weekday(weekday_number):
    return ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"][
        weekday_number
    ]


def format_month(month_number):
    return [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ][month_number]
