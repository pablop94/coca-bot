from django.db import models
from django.utils import timezone
from meals.formatters import format_meal, format_name


class Meal(models.Model):
    done = models.BooleanField(default=False)
    done_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def mark_as_done(self):
        self.done = True
        self.done_at = timezone.now()


class MealItem(models.Model):
    meal = models.ForeignKey("meals.Meal", on_delete=models.CASCADE)
    owner = models.ForeignKey("meals.Participant", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"{format_meal(self.description)} a cargo de {format_name(self.owner.name)}"
        )


class Participant(models.Model):
    name = models.CharField(max_length=50)


class Skip(models.Model):
    pass
