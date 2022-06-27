class NoMealConfigured(Exception):
    def __init__(self):
        self.message = "No hay una comida configurada"


class IncompleteMeal(Exception):
    def __init__(self, message):
        self.message = message


class InvalidDay(Exception):
    pass
