import factory
from datetime import datetime
from meals.models import Meal, Participant, Skip


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant

    name = "John"


class MealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meal

    meal_owner = factory.SubFactory(ParticipantFactory)
    description = "test meal"
    done = False
    done_at = None
    created_at = factory.LazyFunction(datetime.now)


class SkipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skip
