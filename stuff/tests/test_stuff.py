import unittest

from stuff.stuff import Stuff

class IntegralStuff(Stuff):
  unit_size = 3.5
  min_units = 3

class TestIntegralStuff(unittest.TestCase):

  def test_init(self):
    s = IntegralStuff(5)
    self.assertEqual(s.units, 5)
    self.assertEqual(s.size, 17.5)

  def test_init_min_amount(self):
    with self.assertRaises(ValueError):
      s = IntegralStuff(2)

  def test_min_size(self):
    self.assertEqual(IntegralStuff.min_size(), 10.5)

if __name__ == '__main__':
  unittest.main()
