from numbers import Real

from stuff.stuff import Stuff

__all__ = ['RealStuff']

class RealStuff(Stuff):
  """Keeps track of real-valued stuff based on its type.

  There are a number of magic properties that can be set on subtypes to control the
  behavior. The validity of these properties will be verified at type definition time.

  :unit_size: how large each unit of this kind of stuff is. Must be a Real.

  :name: is the name that the type will be registered under in the stuff type registry. If
    it is None, the subtype will not be registered.
  """

  @classmethod
  def _convert_units(cls, units, var='units'):
    """Ensures that the given number of units is of the correct type. Raises an error if
    it is ofthe wrong type. Returns the converted value.

    For RealStuff, the units must be of Real type.
    """
    if not isinstance(units, Real):
      raise TypeError('{} must be a real number'.format(var))
    return float(units)

  @classmethod
  def _check_unit_type(cls, units):
    """Checks if the given units value is of the correct type. Returns true if
    _convert_units would not raise an exception.
    """
    return isinstance(units, Real)

  def divide(self, pieces):
    """Attempts to split this stuff into the specified amount of pieces, with
    equal size for each piece.

    Stuff is conserved by this operation. After this operation, self contains zero stuff,
    and the total stuff in the resulting objects is equal to the amount of stuff that used
    to be in self.

    :self: the stuff to split up.
    :pieces: how many pieces to split into.

    Returns a tuple of stuff with length == pieces which contains the split up stuff from
    self.

    Raises an ValueError if the stuff cannot be split up into that number of pieces.
    """
    if not isinstance(pieces, Integral):
      raise TypeError('number of pieces must be an integer')
    pieces = int(pieces)
    if pieces <= 0:
      raise ValueError('number of pieces must be positive')
    units_per_piece = self._units / pieces
    new_stuff = tuple(self._with_units(units_per_piece) for _ in range(pieces))
    self.clear()
    return new_stuff
