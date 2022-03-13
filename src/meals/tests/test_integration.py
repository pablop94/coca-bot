from django.utils import timezone
from django.test import TestCase
from meals.exceptions import NoMealConfigured
from meals.models import Meal, Participant, Skip
from meals.views import (
    add_meal,
    get_next_meal,
    add_skip,
    get_skip,
    history,
    get_next_meals,
)


class MealTest(TestCase):
    def test_meal_is_added_non_existing_participant(self):
        self.assertEquals(Meal.objects.count(), 0)
        self.assertEquals(Participant.objects.count(), 0)
        add_meal("non-existing", "meal")

        self.assertEquals(Participant.objects.first().name, "non-existing")
        self.assertEquals(Meal.objects.first().description, "meal")

    def test_meal_is_added_existing_participant(self):
        Participant.objects.create(name="existing")
        add_meal("existing", "meal")

        self.assertEquals(Participant.objects.count(), 1)
        self.assertEquals(Participant.objects.first().name, "existing")
        self.assertEquals(Meal.objects.first().description, "meal")

    def test_get_next_meal_returns_first_undone_meal(self):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"),
            description="test",
            done=True,
        )
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test2"), description="test2"
        )

        name, meal, count = get_next_meal()

        self.assertEquals("test2", name)
        self.assertEquals("test2", meal)
        self.assertEquals(0, count)

    def test_get_next_meal_raises_no_meal_configured_if_there_is_no_undone_meal(self):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"),
            description="test",
            done=True,
        )

        with self.assertRaises(NoMealConfigured):
            name, meal, count = get_next_meal()

    def test_get_next_meal_marks_meal_as_done(self):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"), description="test"
        )

        get_next_meal()

        self.assertTrue(Meal.objects.first().done)
        self.assertEquals(timezone.now().day, Meal.objects.first().done_at.day)

    def test_get_next_meal_returns_remaining_count(self):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"), description="test"
        )

        _, _, count = get_next_meal()

        self.assertEquals(0, count)

    def test_get_next_meal_returns_remaining_count_when_there_are_many(self):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"), description="test"
        )
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test2"), description="test2"
        )

        _, _, count = get_next_meal()

        self.assertEquals(1, count)

    def test_meal_is_added_existing_participant_with_uppercase(self):
        Participant.objects.create(name="existing")
        add_meal("Existing", "meal")

        self.assertEquals(Participant.objects.count(), 1)
        self.assertEquals(Meal.objects.first().meal_owner.name, "existing")


class SkipTest(TestCase):
    def test_skip_is_added(self):
        self.assertEquals(Skip.objects.count(), 0)

        add_skip()
        self.assertEquals(Skip.objects.count(), 1)

    def test_get_skip_deletes_it(self):
        Skip.objects.create()
        self.assertEquals(Skip.objects.count(), 1)

        get_skip()
        self.assertEquals(Skip.objects.count(), 0)


class HistoryTest(TestCase):
    def test_history_is_calculated_with_done_meals(self):
        participant1 = Participant.objects.create(name="participant1")
        participant2 = Participant.objects.create(name="participant2")

        Meal.objects.create(meal_owner=participant2, description="test", done=True)
        Meal.objects.create(meal_owner=participant2, description="test")
        Meal.objects.create(meal_owner=participant1, description="test", done=True)
        Meal.objects.create(meal_owner=participant1, description="test")
        Meal.objects.create(meal_owner=participant1, description="test", done=True)

        result = history()

        self.assertEquals(2, len(result))
        self.assertEquals(2, result.first().total_meals)
        self.assertEquals("participant1", result.first().name)
        self.assertEquals(1, result.last().total_meals)
        self.assertEquals("participant2", result.last().name)


class NextMealsTest(TestCase):
    def test_get_next_meals_returns_undone_meals_in_order(self):
        Meal.objects.create(
            meal_owner=Participant.objects.create(name="test"),
            description="test",
            done=True,
        )
        meal2 = Meal.objects.create(
            meal_owner=Participant.objects.create(name="test2"),
            description="description test2",
        )
        meal3 = Meal.objects.create(
            meal_owner=Participant.objects.create(name="test4"),
            description="description test4",
        )
        meal4 = Meal.objects.create(
            meal_owner=Participant.objects.create(name="test3"),
            description="description test3",
        )

        meals = get_next_meals()

        self.assertEquals(3, len(meals))
        self.assertEquals("test2", meals[0][0])
        self.assertEquals("description test2", meals[0][1])
        self.assertEquals(meal2.id, meals[0][2])
        self.assertEquals("test4", meals[1][0])
        self.assertEquals("description test4", meals[1][1])
        self.assertEquals(meal3.id, meals[1][2])
        self.assertEquals("test3", meals[2][0])
        self.assertEquals("description test3", meals[2][1])
        self.assertEquals(meal4.id, meals[2][2])
