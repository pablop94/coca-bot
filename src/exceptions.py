class NoMealConfigured(Exception):
  def __init__(self):
    self.message = "No hay una comida configurada" 
