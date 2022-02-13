from django.db import models


class Meal(models.Model):
    meal_owner = models.ForeignKey("meals.Participant", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Participant(models.Model):
    name = models.CharField(max_length=50)


class Skip(models.Model):
    pass
