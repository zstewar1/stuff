from abc import ABCMeta, abstractmethod
from itertools import islice

from stuff.stuff import Stuff, MetaStuff

__all__ = ['ISized', 'MetaUniqueStuff', 'UniqueStuff']


class ISized(metaclass=ABCMeta):
  """An abstract class for types of unique stuff which should have unique sizes per item.
  """
  @abstractmethod
  def __stuff_size__(self):
    """The size of this item of unique stuff. Return value should be a real."""
    raise NotImplementedError('You must provide an implemenation of __stuff_size__')


class MetaUniqueStuff(MetaStuff):
  """Metaclass for Unique Stuff. Overrides configuration checking of MetaStuff."""

  def __init__(self, name, bases, namespace):
    """Initializes a new UniqueStuff subtype, and registers it if it is named.

    :self: the new type being initialized.
    :name: the name of the new type.
    :bases: list of base types for the new type.
    :namespace: dictionary of the new type's contents.
    """
    # TODO(zstewart): Setup checks for the UniqueStuff type.
    self._register()


class UniqueStuff(Stuff, metaclass=MetaUniqueStuff):
  """Keeps track of unique objects of a particular type.

  There are a number of magic properties that can be set on subtypes to control the
  behavior. The validity of these properties will be verified at type definition time.

  :unit_size: how large each unit of this kind of stuff is. Ignored if the type inherits
    from ISized. Must be a Real, unless unit_type is specified and inherits from ISized,
    in which case it may be set to None.

  :unit_type: is the base type for all items allowed in this class of UniqueStuff. May
    optionally inherit from ISized. If set to None, any object is allowed.

  :name: is the name that the type will be registered under in the stuff type registry. If
    it is None, the subtype will not be registered.
  """
  unit_type = None

  @classmethod
  def _convert_units(cls, units, var='units'):
    """Ensures that the given units are of the appropriate type for this instance. Raises
    an error if it is the wrong type. Returns the converted value.

    For unique stuff, the units must be convertible to a set, and each element must be of
    the unit_type if one was specified.
    """
    try:
      units = set(units)
    except TypeError as err:
      raise TypeError('{} must be convertible to a set'.format(var)) from err
    if cls.unit_type is not None:
      for unit in units:
        if not isinstance(unit, cls.unit_type):
          raise TypeError(
              'every element of {} must be of type {}'.format(var, self.unit_type))
    return units

  @classmethod
  def _check_unit_type(cls, units):
    """Checks if the given units value is of the correct type. Returns true if
    _convert_units would not raise an exception.
    """
    try:
      self._convert_units(units)
    except TypeError:
      return False
    else:
      return True

  def __init__(self, units=()):
    """Create a new stuff of this type with the specified contents.

    :units: An iterable of items to put in this stuff. The contained objects should not
      already be in some other stuff object.
    """
    self._units = self._convert_units(units)

  @property
  def size(self):
    """The total size of the stuff contained in this collection."""
    if not issubclass(self.unit_type, ISized):
      return len(self._units) * self.unit_size
    else:
      return sum(unit.__stuff_size__() for unit in self._units)

  @property
  def units(self):
    """The units contained in this collection."""
    return set(self._units)

  def add(self, units):
    """Add more stuff to the stuff tracker.

    This differs from the addition operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for adding more stuff to be tracked.

    :units: An iterable of stuff to add to this stuff.

    Returns None.
    """
    units = self._convert_units(units)
    self._units |= units

  def remove(self, units):
    """Remove units of stuff from this stuff tracker.

    This differs from the subtraction operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for removing stuff from being
    tracked at all.

    :units: an iterable of stuff to remove from this stuff. This should be a subset of the
      current contents.

    returns None.
    """
    units = self._convert_units(units)
    if units > self._units:
      raise ValueError('can only remove subsets of the contents')
    self._units -= units

  def clear(self):
    """Remove all of the stuff from this tracker, discarding it.

    Returns None.
    """
    self._units.clear()

  def put(self, other):
    """Put stuff from another stuff in this stuff.

    Stuff is conserved by this operation. After this operation the other object contains
    zero stuff, and this object contains all of the stuff.

    :self: our stuff.
    :other: other stuff to take.

    returns self (which now contains all of the stuff)
    """
    if type(self) != type(other):
      raise TypeError('stuff must be of the same type to combine')

    combined = self._units | other._units
    self._units, other._units = combined, set()
    return self

  def combine(self, other):
    """Combine this stuff and other stuff into a new object.

    Stuff is conserved by this operation. After this operation both original objects are
    empty and a new stuff is returned which contains all of the stuff from both originals.

    :self: our stuff.
    :other: other stuff to take.

    returns a new object which contains the combined stuff of the originals.
    """
    if type(self) != type(other):
      raise TypeError('stuff must be of the same type to combine')
    new_object = self._with_units(())
    combined = self._units | other._units
    new_object._units, self._units, other._units = combined, set(), set()
    return new_object

  def separate(self, units):
    """Separate stuff from this stuff and return a new stuff that contains the removed
    stuff.

    Stuff is conserved by this operation. After this operation, self contains less stuff
    than before, and a new Stuff is created which contains the removed stuff.

    :self: our stuff.
    :units: the number of units to separate.

    returns a new stuff of the same type containing part of the original stuff.
    """
    units = self._convert_units(units)
    if units > self._units:
      raise ValueError('stuff to remove must be a subset of the stuff we have')
    remaining = self._units - units
    new_stuff = self._with_units(units)
    self._units = remaining
    return new_stuff

  def divide(self, pieces):
    """Attempts to split this stuff into the specified amount of pieces, with
    approximately equal size for each piece.

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
    base_num_per_piece, remaining = divmod(len(self._units), pieces)

    units = iter(self._units)

    new_stuff = []
    for i in range(pieces):
      units_for_piece = base_num_per_piece
      if i < remaining_units:
        units_for_piece += 1
      new_stuff.append(self._with_units(set(islice(units, units_for_piece))))
    self.clear()
    return tuple(new_stuff)
