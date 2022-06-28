import factory
from datetime import datetime
from meals.models import Meal, MealItem, Participant, Skip


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant

    name = "John"


class MealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meal

    done = False
    done_at = None
    created_at = factory.LazyFunction(datetime.now)


class MealItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealItem

    meal = factory.SubFactory(MealFactory)
    owner = factory.SubFactory(ParticipantFactory)
    description = "test meal"


class SkipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skip
