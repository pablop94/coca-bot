import json 

from unittest import TestCase
from unittest.mock import patch

from src.meals import HISTORY_KEY, MEALS_KEY, SKIP_KEY, add_meal, get_next_meal, history, add_history, get_skip, add_skip
from src.exceptions import NoMealConfigured

class MealTest(TestCase):
  @patch('src.meals.push')
  def test_add_meal(self, pushfn):
    add_meal('test', 'test meal')
    self.assertTrue(pushfn.called)
    pushfn.assert_called_once_with(MEALS_KEY, json.dumps({'name': 'test', 'meal': 'test meal'}))

  @patch('src.meals.pop', side_effect=[json.dumps({'name': 'test', 'meal': 'test meal'})])
  @patch('src.meals.llen', side_effect=[3])
  def test_get_next_meal(self, llenfn, popfn, *args):
    value = get_next_meal()
    self.assertTrue(popfn.called)
    self.assertTrue(llenfn.called)
    self.assertEqual(('test', 'test meal', 3), value)

  @patch('src.meals.pop', side_effect=[None])
  def test_get_next_meal_no_meal(self, popfn):
    with self.assertRaises(NoMealConfigured):
      value = get_next_meal()
    
  @patch('src.meals.get', side_effect=[['test', 'test2', 'test']])
  def test_history(self, get_call):
    result = history()

    get_call.assert_called_once_with(HISTORY_KEY)
    self.assertEqual(['test', 'test2', 'test'], result)

  @patch('src.meals.push')
  def test_add_history(self, push_call):
    add_history('test')

    push_call.assert_called_once_with(HISTORY_KEY, 'test')

  @patch('src.meals.pop', side_effect=['skip'])
  def test_get_skip(self, pop_call):
    result = get_skip()

    pop_call.assert_called_once_with(SKIP_KEY)
    self.assertEqual('skip', result)

  @patch('src.meals.push')
  def test_add_skip(self, push_call):
    add_skip()

    push_call.assert_called_once_with(SKIP_KEY, "skip")