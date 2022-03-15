from django.db import models
from django.utils import timezone


class Meal(models.Model):
    meal_owner = models.ForeignKey("meals.Participant", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    done_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def mark_as_done(self):
        self.done = True
        self.done_at = timezone.now()


class Participant(models.Model):
    name = models.CharField(max_length=50)


class Skip(models.Model):
    pass
