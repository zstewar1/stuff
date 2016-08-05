"""Contains the Stuff class which represents like pieces of arbitrary kinds of stuff.

Operations involving stuff conserve stuff. More stuff can be created through the
constructor or by using the add method.

Typical usage is by defining a new type of stuff by subclassing Stuff.

>>> class MyStuff(Stuff):
...   min_units = 2
...   unit_size = 2.5
...   name = 'my stuff'

This creates a kind of stuff called MyStuff which can only be constructed in blobs of
three at a time, and requires at least 6 items for any nonempty instance.

Instance of MyStuff can be created, and stuff can be moved between them:

>>> x = MyStuff(9) # create 9 new stuff
>>> y = MyStuff(18) # create 18 new stuff

>>> (y - 6) >> x # Remove 6 stuff from y, and send it to x.
[15 my stuff]
>>> y
[12 my stuff]
>>> x
[15 my stuff]

Supported operations include:
  - Addition: combine two stuff into a new stuff, emptying the originals in the process.
  - In-Place Addition: put all the stuff from one stuff into another stuff.
  - Subtraction: split off some amount of stuff into a new object.
  - Division: split split stuff into a tuple of smaller bits of stuff.
  - Modulo: check if a split would be valid.
  - Left Shift: Put all the stuff in the left operand.
  - Right Shift: Put all the stuff in the right operand.

Stuff is type safe, so every new stuff subtype cannot be mixed with any other type of
stuff.
"""

from numbers import Integral, Real
import threading

__all__ = ['get_stuff', 'MetaStuff', 'Stuff']

_REGISTRY_LOCK = threading.RLock()
_REGISTRY = {}

def get_stuff(name):
  """Attempt to get the type of stuff with the given registry name. Returns none if no
  such type of stuff exists.

  :name: the name of the type of stuff ot look up.
  """
  with _REGISTRY_LOCK:
    return _REGISTRY.get(name)


class MetaStuff(type):
  """Metaclass for Stuff objects. Handles things like class-level properties and
  registration of Stuff types."""

  def __init__(self, name, bases, namespace):
    """Initializes a new stuff subtype, and registers it if it is named.

    :self: the new type being initialized.
    :name: name of the new type.
    :bases: list of base types for the new type.
    :namespace: dictionary of the new type's contents.
    """
    self.min_units = self._convert_units(self.min_units, var='min_units')
    if not isinstance(self.unit_size, Real):
      raise TypeError('unit_size must be a real number')
    self.unit_size = float(self.unit_size)
    if self.name is not None:
      if not isinstance(self.name, str):
        raise TypeError('name must be a string')
      self.name = str(self.name)

    if self.min_units <= 0:
      raise ValueError('min units of stuff must be positive')
    if self.unit_size < 0:
      raise ValueError('unit_size of stuff must nonnegative')

    self._register()

  def _register(self):
    name = self.name
    if name is not None:
      with _REGISTRY_LOCK:
        if name in _REGISTRY:
          raise TypeError('Attempting to create already existing type of stuff')
        _REGISTRY[name] = self


class Stuff(object, metaclass=MetaStuff):
  """Keeps track of a kind of stuff based on its type.

  There are a number of magic properties that can be set on subtypes to control the
  behavior. The validity of these properties will be verified at type definition time.

  :min_units: is the least number of units of stuff that an individual object of this type
    is allowed to contain. Defaults to 1. (Objects are always allowed to contain zero
    stuff, no matter the set minimum. The minimum applies to any nonzero amount of stuff).

  :unit_size: how large each unit of this kind of stuff is. Must be a Real.

  :name: is the name that the type will be registered under in the stuff type registry. If
    it is None, the subtype will not be registered.
  """
  min_units = 1

  unit_size = 1.0

  name = None

  @classmethod
  def min_size(cls):
    """The minimum size of stuff an instance can contain given the minimum quantity and
    unit_size.
    """
    return cls.min_units * cls.unit_size

  @classmethod
  def _convert_units(cls, units, var='units'):
    """Ensures that the given number of units is the correct type. Raises an error if it
    is the wrong type. Returns the converted value.

    For base stuff, the units must be of Integral type.
    """
    if not isinstance(units, Integral):
      raise TypeError('{} must be an integer'.format(var))
    return int(units)

  @classmethod
  def _check_unit_type(cls, units):
    """Checks if the given units value is of the correct type. Returns true if
    _convert_units would not raise an exception.
    """
    return isinstance(units, Integral)

  def __init__(self, units=0):
    """Creates new stuff of this type.

    :units: How many units of new stuff this object should contain.
    """
    units = self._convert_units(units)
    if units < 0:
      raise ValueError('amount of stuff must be nonnegative')
    if units != 0 and units < self.min_units:
      raise ValueError('not enough stuff for minimum amount')
    self._units = units

  @property
  def size(self):
    """The total size of the stuff contained in this collection."""
    return self._units * self.unit_size

  @property
  def units(self):
    """The number of units of stuff contained in this collection."""
    return self._units

  def add(self, units):
    """Add more stuff to the stuff tracker.

    This differs from the addition operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for adding more stuff to be tracked.

    :units: how many whole units of stuff to add.

    returns the new number of units of stuff being held.
    """
    units = self._convert_units(units)
    if units < 0:
      raise ValueError('can only add positive amounts of stuff')
    self._units += units
    return self.units

  def remove(self, units):
    """Remove units of stuff rom this stuff tracker.

    This differs from the subtraction operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for removing stuff from being
    tracked at all.

    :units: how many units to get rid of.

    returns how many units of stuff are left.
    """
    units = self._convert_units(units)
    if units < 0:
      raise ValueError('can only remove positive amounts of stuff')
    if units > self._units:
      raise ValueError('cannot remove more stuff than we have')
    remaining = self._units - units
    if remaining != 0 and remaining < self.min_units:
      raise ValueError('does not leave enough stuff behind')
    self._units = remaining
    return remaining

  def clear(self):
    """Remove all of the stuff from this tracker, discarding it.

    returns how many units were removed.
    """
    units = self._units
    self._units = self._convert_units(0)
    return units

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

    total_units = self._units + other._units
    self._units, other._units = total_units, other._convert_units(0)
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
    new_object = self._with_units(0)
    total_units = self._units + other._units
    zero = self._convert_units(0)
    new_object._units, self._units, other._units = total_units, zero, zero
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
    if units < 0:
      raise ValueError('can only separate out a positive amount of stuff')
    if units > self._units:
      raise ValueError('cannot separate more units than we have')
    if units != 0 and units < self.min_units:
      raise ValueError('must separate at least the min_units')
    remaining = self._units - units
    if remaining != 0 and remaining < self.min_units:
      raise ValueError('does not leave enough stuff behind')
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
    base_units_per_piece, remaining_units = divmod(self._units, pieces)
    if base_units_per_piece < self.min_units:
      raise ValueError('not enough stuff to make the requested number of pieces')
    new_stuff = []
    for i in range(pieces):
      units_for_piece = base_units_per_piece
      if i < remaining_units:
        units_for_piece += 1
      new_stuff.append(self._with_units(units_for_piece))
    self.clear()
    return tuple(new_stuff)

  def _with_units(self, units):
    """Create a new stuff with the specified number of units.

    Allows subtypes which take additional required constructor arguments to provide
    sensible defaults based on this instance without having to reimplement all of the
    operators.

    :units: the number of units of stuff the new instance should hold.
    """
    return type(self)(units=units)

  # Implementation of the Data Model for this type.
  def __bool__(self):
    """Returns true if this object contains any stuff."""
    return bool(self._units)

  def __str__(self):
    """Return a representation of this object in the form "{units} {typename}"."""
    return '{} {}'.format(self.units, self.name or type(self).__name__)

  def __repr__(self):
    """Return a representation of this object in the form "[{units} {typename}]"."""
    return '[' + str(self) + ']'

  def __add__(self, other):
    """Combine this stuff and other stuff into a new object.

    Stuff is conserved by this operation. After this operation both original objects are
    empty and a new stuff is returned which contains all of the stuff from both originals.

    :self: our stuff.
    :other: other stuff to take.

    returns a new object which contains the combined stuff of the originals.
    """
    if type(self) != type(other):
      return NotImplemented
    return self.combine(other)

  def __iadd__(self, other):
    """Put stuff from another stuff in this stuff.

    Stuff is conserved by this operation. After this operation the other object contains
    zero stuff, and this object contains all of the stuff.

    :self: our stuff.
    :other: other stuff to take.

    returns self (which now contains all of the stuff)
    """
    if type(self) != type(other):
      return NotImplemented
    return self.put(other)

  def __sub__(self, units):
    """Remove stuff from this stuff and return a new stuff that contains the removed
    stuff. Warning: Does not do normal subtraction. Modifies self in place.

    Stuff is conserved by this operation. After this operation, self contains less stuff,
    and a new stuff is returned which contains the stuff which was removed.

    :self: our stuff.
    :units: how many units of stuff should be removed.

    returns a new stuff of the same type containing part of the original stuff.
    """
    if not self._check_unit_type(units):
      return NotImplemented
    return self.separate(units)

  def __isub__(self, *args):
    """Returns not-implmented because in-place subtraction of stuff is not allowed.
    Subtracting stuff changes the stuff being subtracted from and returns new stuff
    containing the stuff that was removed. With in-place subraction, the resulting stuff
    would replace the original stuff, or the resulting stuff would be discarded, and
    either way stuff would be gone forever. If you really want this behavior, use a
    regular operation with assignment.
    """
    raise NotImplementedError('In Place Subtraction is not supportted for Stuff')

  def __floordiv__(self, pieces):
    if not isinstance(pieces, Integral):
      return NotImplemented
    return self.divide(pieces)

  def __mod__(self, pieces):
    """Tests whether this stuff can be broken into a given number of pieces.

    :self: the stuff.
    :pieces: the number of pieces.
    """
    if not isinstance(pieces, Integral):
      return NotImplemented
    pieces = int(pieces)
    if pieces <= 0:
      raise ValueError('number of pieces must be positive')
    # should be safe for both int and float, since the ceiling of dividing an int by an
    # int is always less than the next higher int.
    units_per_piece = self._units / pieces
    return base_units_per_piece >= self.min_units

  def __lshift__(self, other):
    """Shift all the stuff into the left argument. Return the object that now contains all
    of the stuff.

    Stuff is conserved by this operation. After this operation, other contains zero stuff,
    and self contains all of the stuff.

    :self: our stuff.
    :other: stuff to take.
    """
    if type(self) != type(other):
      return NotImplemented
    return self.combine(other)

  def __rshift__(self, other):
    """Shift all the stuff into the right argument. Return the object that now contains
    all of the stuff.


    Stuff is conserved by this operation. After this operation, other contains all of the
    stuff, and self contains zero stuff.

    :self: our stuff to give away.
    :other: stuff to add to.
    """
    if type(self) != type(other):
      return NotImplemented
    return other.combine(self)
