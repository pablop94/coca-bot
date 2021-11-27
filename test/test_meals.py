import json 

from unittest import TestCase
from unittest.mock import patch

from src.meals import add_meal, get_next_meal
from src.exceptions import NoMealConfigured

class MealTest(TestCase):
  @patch('src.meals.push')
  def test_add_meal(self, pushfn):
    add_meal('test', 'test meal')
    self.assertTrue(pushfn.called)
    pushfn.assert_called_once_with(json.dumps({'name': 'test', 'meal': 'test meal'}))

  @patch('src.meals.pop', side_effect=[json.dumps({'name': 'test', 'meal': 'test meal'})])
  def test_get_next_meal(self, popfn):
    value = get_next_meal()
    self.assertTrue(popfn.called)
    self.assertEqual(('test', 'test meal'), value)

  @patch('src.meals.pop', side_effect=[None])
  def test_get_next_meal_no_meal(self, popfn):
    with self.assertRaises(NoMealConfigured):
      value = get_next_meal()
    