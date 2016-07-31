"""Contains the Stuff class which represents like pieces of arbitrary kinds of stuff.

Operations involving stuff conserve stuff, so the only way to get more of a particular
kind of stuff is through the type's constructor.

Typical usage is by defining a new type of stuff by subclassing Stuff.

>>> class MyStuff(Stuff, min_amount=6, granularity=3):
...   pass

This creates a kind of stuff called MyStuff which can only be constructed in blobs of
three at a time, and requires at least 6 items for any nonempty instance.

Instance of MyStuff can be created, and stuff can be moved between them:

>>> x = MyStuff(9) # create 9 new stuff
>>> y = MyStuff(18) # create 18 new stuff

>>> (y - 6) >> x # Remove 6 stuff from y, and send it to x.
[15 of MyStuff]
>>> y
[12 of MyStuff]
>>> x
[15 of MyStuff]

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

import math
import threading

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
  """Metaclalss for Stuff objects. Handles things like class-level properties and
  registration of Stuff types."""

  def __init__(self, name, bases, namespace):
    """Creates a new stuff subtype.

    :self: the new type being initialized
    :name: name of the new type.
    :bases: list of base types for the new type.
    :namespace: dictionary of the new type's contents.
    """
    if not isinstance(self.min_amount, int):
      raise TypeError('min_amount must be an integer')
    if not isinstance(self.granularity, int):
      raise TypeError('granularity must be an integer')
    self.min_amount = int(self.min_amount)
    self.granularity = int(self.granularity)
    if self.name is not None:
      if not isinstance(self.name, str):
        raise TypeError('name must be a string')
      self.name = str(self.name)

    if self.min_amount < 1:
      raise ValueError('min amount of stuff must be at least 1')
    if self.granularity < 1:
      raise ValueError('granularity of stuff must be at least 1')

    name = self.name
    if name is not None:
      with _REGISTRY_LOCK:
        if name in _REGISTRY:
          raise TypeError('Attempting to create already existing type of stuff')
        _REGISTRY[name] = self


class Stuff(object, metaclass=MetaStuff):
  """Keeps track of a kind of stuff based on its type.

  Includes facilities for controlling how granular tracking should be (i.e. what is the
  smallest unit that can be split out). These are controlled by setting magic properties
  on the class instance. The validity of these properties will be verified at type
  definition time.

  :min_amount: is the least amount of stuff that an individual object of this type is
    allowed to contain. Defaults to 1. (Objects are always allowed to contain zero stuff,
    no matter the set minimum. The minimum applies to any nonzero amount of stuff).

  :granularity: is the divisibility of objects of this type. When breaking down into
    chunks, objects of this type must contain a multiple of this amount of stuff. Defaults
    to 1.

  :name: is the name that the type will be registered under in the stuff type registry. If
    it is None, the subtype will not be registered.
  """
  min_amount = 1

  granularity = 1

  name = None

  @classmethod
  def smallest_allowed_amount(cls):
    """The minimum amount of stuff an instance can contain given the minimum quantity and
    granularity.
    """
    return cls.least_allowed_units * cls.granularity

  @classmethod
  def least_allowed_units(cls):
    """The minimum number of units of stuff an instance can contain given the minimum
    quantity and granularity.
    """
    return math.ceil(cls.min_amount / cls.granularity)

  def __init__(self, amount=0, *, use_units=False):
    """Creates new stuff of this type.

    :amount: How much new stuff should be contained in the new object.
    :use_units: If true, amount is taken to be in indivisible units of stuff rather than
      an absolue amount.
    """
    self._granular_units = 0
    if use_units:
      self.add_units(amount)
    else:
      self.add(amount)

  @property
  def amount(self):
    """The total amount of stuff contained in this collection."""
    return self._granular_units * self.granularity

  @property
  def units(self):
    """The number of units of stuff contained in this collection."""
    return self._granular_units

  def add_units(self, units):
    """Add more stuff to the stuff tracker.

    This differs from the addition operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for adding more stuff to be tracked.

    :units: how many whole units of stuff to add.

    returns the new number of units of stuff being held.
    """
    if not isinstance(units, int):
      raise TypeError('units must be an integer')
    if units < 0:
      raise ValueError('can only add positive amounts of stuff')
    self._granular_units += units
    return self.units

  def add(self, amount):
    """Add more stuff to the stuff tracker.

    This differs from the addition operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for adding more stuff to be tracked.

    :amount: how much new stuff to keep track of.

    returns the new amount of stuff being held.
    """
    if not isinstance(amount, int):
      raise TypeError('amount must be an integer')
    if amount % self.granularity != 0:
      raise ValueError('amount is not divisible by the granularity')
    self.add_units(amount // self.granularity)
    return self.amount

  def remove_units(self, units):
    """Remove units of stuff rom this stuff tracker.

    This differs from the subtraction operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for removing stuff from being
    tracked at all.

    :units: how many units to get rid of.

    returns how many units of stuff are left.
    """
    if not isinstance(units, int):
      raise TypeError('units must be an integer')
    if units < 0:
      raise ValueError('can only remove positive amounts of stuff')
    if units > self._granular_units:
      raise ValueError('cannot remove more stuff than we have')
    remaining = self._granular_units - units
    if remaining != 0 and remaining < self.least_allowed_units():
      raise ValueError('does not leave enough stuff behind')
    self._granular_units = remaining
    return remaining

  def remove(self, amount):
    """Remove an amount of stuff from this tracker.

    This differs from the subtraction operator in that the operators are for moving stuff
    around while keeping track of it, whereas this is for removing stuff from being
    tracked at all.

    :amount: how much new stuff to get rid of.

    returns how much stuff is left.
    """
    if not isinstance(amount, int):
      raise TypeError('amount must be an integer')
    if amount % self.granularity != 0:
      raise ValueError('amount is not divisible by the granularity')
    self.remove_units(amount // granularity)
    return self.amount

  def clear_units(self):
    """Remove all of the stuff from this tracker, discarding it.

    returns how many units were removed.
    """
    units = self._granular_units
    self._granular_units = 0
    return units

  def clear(self):
    """Remove all of the stuff from this tracker, discarding it.

    returns how much stuff was removed.
    """
    amount = self.amount
    self._granular_units = 0
    return amount

  def combine(self, other):
    """Put stuff from another stuff in this stuff.

    Stuff is conserved by this operation. After this operation the other object contains
    zero stuff, and this object contains all of the stuff.

    :self: our stuff.
    :other: other stuff to take.

    returns self (which now contains all of the stuff)
    """
    if type(self) != type(other):
      raise TypeError('stuff must be of the same type to combine')

    total_units = self._granular_units + other._granular_units
    self._granular_units, other._granular_units = total_units, 0
    return self

  def separate_units(self, units):
    """Separate stuff from this stuff and return a new stuff that contains the removed
    stuff.

    Stuff is conserved by this operation. After this operation, self contains less stuff
    than before, and a new Stuff is created which contains the removed stuff.

    :self: our stuff.
    :units: the number of units to separate.

    returns a new stuff of the same type containing part of the original stuff.
    """
    if not isinstance(units, int):
      raise TypeError('units of stuff to separate must be an integer')
    if units < 0:
      raise ValueError('can only separate out a positive amount of stuff')
    if units > self._granular_units:
      raise ValueError('cannot separate more units than we have')
    if units < self.least_allowed_units():
      raise ValueError('must separate at least the min_amount worth of units')
    remaining = self._granular_units - units
    if remaining != 0 and remaining < self.least_allowed_units():
      raise ValueError('does not leave enough stuff behind')
    new_stuff = self._with_units(units)
    self._granular_units = remaining
    return new_stuff

  def separate(self, amount):
    """Separate stuff from this stuff and return a new stuff that contains the removed
    stuff.

    Stuff is conserved by this operation. After this operation, self contains "amount"
    less stuff than before, and a new Stuff is created which contains "amount" stuff.

    :self: our stuff.
    :amount: how much stuff to split off into the new instance.

    returns a new stuff of the same type containing part of the original stuff.
    """
    if not isinstance(amount, int):
      raise TypeError('amount of stuff to separate must be an integer')
    if amount % self.granularity != 0:
      raise ValueError('amount is not divisibile by the granularity')
    return self.separate_units(amount // self.granularity)

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
    if not isinstance(pieces, int):
      raise TypeError('number of pieces must be an integer')
    if pieces <= 0:
      raise ValueError('number of pieces must be positive')
    base_units_per_piece, remaining_units = divmod(self._granular_units, pieces)
    if base_units_per_piece < self.least_allowed_units():
      raise ValueError('not enough stuff to make the requested number of pieces')
    new_stuff = []
    for i in range(pieces):
      units_for_piece = base_units_per_piece
      if i < remaining_units:
        units_for_piece += 1
      new_stuff.append(self._with_units(units_for_piece))

    self._granular_units = 0
    return tuple(new_stuff)

  def _with_units(self, units):
    """Create a new stuff with the specified number of units.

    Allows subtypes which take additional required constructor arguments to provide
    sensible defaults based on this instance without having to reimplement all of the
    operators.

    :units: the number of units of stuff the new instance should hold.
    """
    return type(self)(amount=units, use_units=True)

  # Implementation of the Data Model for this type.
  def __bool__(self):
    """Returns true if this object contains any stuff."""
    return bool(self.amount)

  def __str__(self):
    """Return a representation of this object in the form "{amount} {typename}"."""
    return '{} of {}'.format(self.amount, self.name or type(self).__name__)

  def __repr__(self):
    """Return a representation of this object in the form "[{amount} {typename}]"."""
    return '[' + str(self) + ']'

  def __add__(self, other):
    """Put stuff from another stuff in this stuff.

    Stuff is conserved by this operation. After this operation the other object contains
    zero stuff, and this object contains all of the stuff.

    :self: our stuff.
    :other: other stuff to take.

    returns self (which now contains all of the stuff)
    """
    if type(self) != type(other):
      return NotImplemented
    return self.combine(other)

  def __sub__(self, amount):
    """Remove stuff from this stuff and return a new stuff that contains the removed
    stuff. Warning: Does not do normal subtraction. Modifies self in place.

    Stuff is conserved by this operation. After this operation, self contains "amount"
    less stuff than before, and a new Stuff is created which contains "amount" stuff.

    :self: our stuff.
    :amount: how much stuff to split off into the new instance.

    returns a new stuff of the same type containing part of the original stuff.
    """
    if not isinstance(amount, int):
      return NotImplemented
    return self.separate(amount)

  def __isub__(self, *args):
    """Returns not-implmented because in-place subtraction of stuff is not allowed.
    Subtracting stuff changes the stuff being subtracted from and returns new stuff
    containing the stuff that was removed. With in-place subraction, the resulting stuff
    would replace the original stuff, or the resulting stuff would be discarded, and
    either way stuff would be gone forever. If you really want this behavior, use a
    regular operation with assignment.
    """
    return NotImplemented

  def __floordiv__(self, pieces):
    if not isinstance(pieces, int):
      return NotImplemented
    return self.divide(pieces)

  def __mod__(self, pieces):
    """Tests whether this stuff can be broken into a given number of pieces.

    :self: the stuff.
    :pieces: the number of pieces.
    """
    if not isinstance(pieces, int):
      return NotImplemented
    if pieces <= 0:
      raise ValueError('number of pieces must be positive')
    base_units_per_piece = self._granular_units // pieces
    return base_units_per_piece >= self.least_allowed_units()

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
