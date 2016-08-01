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

  def test_clear(self):
    """check clear works normally"""
    s = IntegralStuff(8)
    result = s.clear()
    self.assertEqual(result, 8)
    self.assertEqual(s.units, 0)

  def test_put(self):
    """test normal put (both .put() and +=)"""
    s = IntegralStuff(8)
    o = IntegralStuff(4)
    res = s.put(o)
    self.assertEqual(s.units, 12)
    self.assertEqual(o.units, 0)
    self.assertIs(res, s)

    s = IntegralStuff(8)
    o = IntegralStuff(4)
    s += o
    self.assertEqual(s.units, 12)
    self.assertEqual(o.units, 0)

  def test_put_wrong_type(self):
    """ensure has correct type-checking"""
    s = IntegralStuff(8)
    with self.assertRaises(TypeError):
      s.put(2)
    self.assertEqual(s.units, 8)

    s = IntegralStuff(8)
    with self.assertRaises(TypeError):
      s += 2
    self.assertEqual(s.units, 8)

    class WrongTypeStuff(Stuff):
      unit_size = 3.5
      min_units = 3

    s = IntegralStuff(8)
    o = WrongTypeStuff(4)
    with self.assertRaises(TypeError):
      s.put(o)
    self.assertEqual(s.units, 8)

    s = IntegralStuff(8)
    o = WrongTypeStuff(4)
    with self.assertRaises(TypeError):
      s += o
    self.assertEqual(s.units, 8)

    # We still don't consider it valid if it's a subtype.
    class WrongTypeSubtype(IntegralStuff):
      unit_size = 4.75
      min_units = 1

    s = IntegralStuff(8)
    o = WrongTypeSubtype(4)
    with self.assertRaises(TypeError):
      s.put(o)
    self.assertEqual(s.units, 8)

    s = IntegralStuff(8)
    o = WrongTypeSubtype(4)
    with self.assertRaises(TypeError):
      s += o
    self.assertEqual(s.units, 8)

    s = WrongTypeSubtype(8)
    o = IntegralStuff(4)
    with self.assertRaises(TypeError):
      s.put(o)
    self.assertEqual(s.units, 8)

    s = WrongTypeSubtype(8)
    o = IntegralStuff(4)
    with self.assertRaises(TypeError):
      s += o
    self.assertEqual(s.units, 8)

  def test_combine(self):
    """check normal combination (both .combine() and +)"""
    s = IntegralStuff(8)
    o = IntegralStuff(4)
    res = s.combine(o)
    self.assertEqual(s.units, 0)
    self.assertEqual(o.units, 0)
    self.assertEqual(res.units, 12)

    s = IntegralStuff(8)
    o = IntegralStuff(4)
    res = s + o
    self.assertEqual(s.units, 0)
    self.assertEqual(o.units, 0)
    self.assertEqual(res.units, 12)

  def test_combine_wrong_type(self):
    s = IntegralStuff(8)
    with self.assertRaises(TypeError):
      s.combine(2)
    self.assertEqual(s.units, 8)

    s = IntegralStuff(8)
    with self.assertRaises(TypeError):
      s + 2
    self.assertEqual(s.units, 8)

    class WrongTypeStuff(Stuff):
      unit_size = 3.5
      min_units = 3

    s = IntegralStuff(8)
    o = WrongTypeStuff(4)
    with self.assertRaises(TypeError):
      s.combine(o)
    self.assertEqual(s.units, 8)

    s = IntegralStuff(8)
    o = WrongTypeStuff(4)
    with self.assertRaises(TypeError):
      s + o
    self.assertEqual(s.units, 8)

    # We still don't consider it valid if it's a subtype.
    class WrongTypeSubtype(IntegralStuff):
      unit_size = 4.75
      min_units = 1

    s = IntegralStuff(8)
    o = WrongTypeSubtype(4)
    with self.assertRaises(TypeError):
      s.combine(o)
    self.assertEqual(s.units, 8)

    s = IntegralStuff(8)
    o = WrongTypeSubtype(4)
    with self.assertRaises(TypeError):
      s + o
    self.assertEqual(s.units, 8)

    s = WrongTypeSubtype(8)
    o = IntegralStuff(4)
    with self.assertRaises(TypeError):
      s.combine(o)
    self.assertEqual(s.units, 8)

    s = WrongTypeSubtype(8)
    o = IntegralStuff(4)
    with self.assertRaises(TypeError):
      s + o
    self.assertEqual(s.units, 8)


if __name__ == '__main__':
  unittest.main()
