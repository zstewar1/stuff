import unittest

from stuff.stuff import Stuff

class IntegralStuff(Stuff):
  unit_size = 3.5
  min_units = 3

class TestIntegralStuff(unittest.TestCase):

  def test_init(self):
    """creation assigns units, make sure size gives correct value"""
    s = IntegralStuff(5)
    self.assertEqual(s.units, 5)
    self.assertEqual(s.size, 17.5)

  def test_init_min_units(self):
    """make sure min units is enforced"""
    with self.assertRaises(ValueError):
      # Below the limit
      s = IntegralStuff(2)
    # Exactly the limit
    s = IntegralStuff(3)
    self.assertEqual(s.units, 3)
    # nothing
    s = IntegralStuff(0)
    self.assertEqual(s.units, 0)

  def test_min_size(self):
    """check the given min_size value"""
    self.assertEqual(IntegralStuff.min_size(), 10.5)

  def test_add(self):
    """normal addition"""
    s = IntegralStuff(5)
    current = s.add(3)
    self.assertEqual(current, 8)
    self.assertEqual(s.units, 8)

  def test_add_negative(self):
    """make sure nonnegative addition is enforced"""
    s = IntegralStuff(5)
    with self.assertRaises(ValueError):
      s.add(-3)
    self.assertEqual(s.units, 5)

  def test_add_wrong_type(self):
    """make sure type checking is enforced"""
    s = IntegralStuff(5)
    with self.assertRaises(TypeError):
      s.add(3.0)
    with self.assertRaises(TypeError):
      s.add('sdfsd')
    self.assertEqual(s.units, 5)

  def test_remove(self):
    """normal removal"""
    s = IntegralStuff(30)
    current = s.remove(8)
    self.assertEqual(current, 22)
    self.assertEqual(s.units, 22)

  def test_remove_negative(self):
    """ensure that nonnegative removal is enforced"""
    s = IntegralStuff(30)
    with self.assertRaises(ValueError):
      s.remove(-4)
    self.assertEqual(s.units, 30)

  def test_remove_wrong_type(self):
    """make sure type checking is enforced"""
    s = IntegralStuff(30)
    with self.assertRaises(TypeError):
      s.remove(3.0)
    with self.assertRaises(TypeError):
      s.remove('sdlfkj')
    self.assertEqual(s.units, 30)

  def test_remove_too_much(self):
    """various cases of too many units being removed"""
    s = IntegralStuff(30)
    with self.assertRaises(ValueError):
      # Remove more than the total.
      s.remove(40)
    with self.assertRaises(ValueError):
      # Remove to below the min_units
      s.remove(28)
    self.assertEqual(s.units, 30)
    # Remove to exactly the limit
    current = s.remove(27)
    self.assertEqual(current, 3)
    self.assertEqual(s.units, 3)
    # Remove the whole amount
    s = IntegralStuff(30)
    current = s.remove(30)
    self.assertEqual(current, 0)
    self.assertEqual(s.units, 0)


if __name__ == '__main__':
  unittest.main()
