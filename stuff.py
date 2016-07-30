"""Contains the Stuff class which represents like pieces of arbitrary kinds of stuff.

Operations involving stuff conserve stuff, so

"""


class MetaStuff(type):
  """Metaclalss for Stuff objects. Handles things like class-level properties and
  registration of Stuff types."""

  @property
  def min_amount(self):
    """minimum amount of stuff allowed by this type."""
    return self._min_amount

  @property
  def granularity(self):
    """minimum granularity of this type of stuff."""
    return self._granularity

  @property
  def name(self):
    """name of the type of stuff."""
    return self._name

  @property
  def smallest_allowed_amount(self):
    """The minimum amount of stuff an instance can contain given the minimum quantity and
    granularity.
    """
    if self.min_amount <= self.granularity:
      return self.granularity
    else:
      return math.ceil(self.min_amount / self.granularity) * self.granularity

  def __new__(
      cls, name, bases, namespace, min_amount=1, granularity=1, registry_name=None):
    """Creates a new stuff subtype.

    :cls: the meta type of the new type.
    :name: name of the new type.
    :bases: list of base types for the new type.
    :namespace: dictionary of the new type's contents.
    :min_amount: min amount of stuff the new type allows.
    :granularity: size of packets of stuff.
    :registry_name: alternate name for the new kind of stuff. Used for registration and
      in names. Defaults to the name of the stuff type.
    """
    if not isinstance(min_amount, int):
      raise TypeError('min_amount must be an integer')
    if not isinstance(granularity, int):
      raise TypeError('granularity must be an integer')
    min_amount = int(min_amount)
    granularity = int(granularity)
    if registry_name is not None:
      if not isinstance(registry_name, str):
        raise TypeError('name must be a string')
    else:
      registry_name = name

    if min_amount < 1:
      raise ValueError('min amount of stuff must be at least 1')
    if granularity < 1:
      raise ValueError('granularity of stuff must be at least 1')

    # Actual size and granularity data are only "hidden" in underscore variables.
    # (Closure-based properties are possible but not really worth it.
    namespace['_min_amount'] = min_amount
    namespace['_granularity'] = granularity
    namespace['_name'] = registry_name

    # Provide both class an instance level property accessors without having to duplicate
    # the accessor code. (Because @property does't work on @classmethod and @classmethod
    # doesn't work on @property)
    provide_methods = [
        'min_amount',
        'granularity',
        'name',
        'smallest_allowed_amount',
    ]

    for method in provide_methods:
      if not any(hasattr(base, method) for base in bases):
        namespace[method] = getattr(MetaStuff, method)

    return super().__new__(cls, name, bases, namespace)

  def __init__(self, name, bases, namespace, **kwds):
    super().__init__(name, bases, namespace)


class Stuff(object, metaclass=MetaStuff):
  """Keeps track of a kind of stuff based on its type.

  Includes facilities for controlling how granular tracking should be (i.e. what is the
  smallest unit that can be split out). These are controlled by setting keyword arguments to the type constructor.

  :min_amount: is the least amount of stuff that an individual object of this type is
    allowed to contain. Defaults to 1. (Objects are always allowed to contain zero stuff,
    no matter the set minimum. The minimum applies to any nonzero amount of stuff).

  :granularity: is the divisibility of objects of this type. When breaking down into
    chunks, objects of this type must contain a multiple of this amount of stuff. Defaults
    to 1.
  """

  def __init__(self, amount=0):
    """Creates new stuff of this type.

    :amount: How much new stuff is created. Will be converted to an integer.
    """
    if not isinstance(amount, int):
      raise TypeError('amount must be an integer')
    # convert to avoid dealing with subtypes.
    amount = int(amount)

    if amount % self.granularity != 0:
      raise ValueError('amount is not divisibile by the granularity')
    if amount < self.min_amount and amount != 0:
      raise ValueError('amount is less than the minimum amount')

    self._granular_units = amount // self.granularity

  @property
  def amount(self):
    """The total amount of stuff contained in this collection."""
    return self._granular_units * self.granularity

  def _with_amount(self, amount):
    """Create a new stuff with the specified amount.

    Allows subtypes which take additional required constructor arguments to provide
    sensible defaults based on this instance without having to reimplement all of the
    operators.

    :amount: the amount of stuff the new instance should hold.
    """
    return type(self)(amount=amount)

  # Implementation of the Data Model for this type.
  def __bool__(self):
    """Returns true if this object contains any stuff."""
    return bool(self.amount)

  def __str__(self):
    """Return a representation of this object in the form "{amount} {typename}"."""
    return '{} {}'.format(self.amount, self.name)

  def __repr__(self):
    """Return a representation of this object in the form "[{amount} {typename}]"."""
    return '[' + str(self) + ']'

  def __add__(self, other):
    """Create a new stuff which contains all the stuff that used to be in this stuff and
    the other stuff.

    Stuff is conserved by this operation. After this operation the original 2 objects
    contain zero stuff, and the resulting object contains all of the stuff.

    :self: our stuff.
    :other: other stuff. must be the same type of stuff.
    """
    if type(self) != type(other):
      return NotImplemented

    total_stuff = self.amount + other.amount
    new_stuff = self._with_amount(total_stuff)
    self._granular_units, other._granular_units = 0, 0
    return new_stuff

  def __iadd__(self, other):
    """Add stuff from another stuff to this stuff.

    Stuff is conserved by this operation. After this operation the other object contains
    zero stuff, and this object contains all of the stuff.

    :self: our stuff.
    :other: other stuff to take.
    """
    if type(self) != type(other):
      return NotImplemented

    total_units = self._granular_units + other._granular_units
    self._granular_units, other._granular_units = total_units, 0
    return self

  def __sub__(self, amount):
    """Remove stuff from this stuff and return a new stuff that contains the removed
    stuff. Warning: Does not do normal subtraction. Modifies self in place.

    Stuff is conserved by this operation. After this operation, self contains "amount"
    less stuff than before, and a new Stuff is created which contains "amount" stuff.

    :self: our stuff.
    :amount: how much stuff to split off into the new instance.
    """
    if not isinstance(amount, int):
      return NotImplemented
    amount = int(amount)
    if amount % self.granularity != 0:
      raise ValueError('amount is not divisibile by the granularity')

    if amount != 0 and amount < self.min_amount:
      raise ValueError('removal is not large enough to satisfy minimum amount')
    if self.amount != amount and self.amount - amount < self.min_amount:
      raise ValueError('removal does not leave behind enough stuff for this instance')

    new_granular_units = (self.amount - amount) // self.granularity
    new_stuff = self._with_amount(amount)
    self._granular_units = new_granular_units
    return new_stuff

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
      return NotImplemented
    pieces = int(pieces)
    base_units_per_piece, remaining_units = divmod(self._granular_units, pieces)
    if base_units_per_piece * self.granularity < self.min_amount:
      raise ValueError('Not enough stuff to meet minimum amount requirements')

    new_stuff = []
    for i in range(pieces):
      units_for_piece = base_units_per_piece
      if i < remaining_units:
        units_for_piece += 1
      new_stuff.append(self._with_amount(units_for_piece * self.granularity))

    self._granular_units = 0
    return tuple(new_stuff)

  def __mod__(self, pieces):
    """Tests whether this stuff can be broken into a given number of pieces.

    :self: the stuff.
    :pieces: the number of pieces.
    """
    if not isinstance(pieces, int):
      return NotImplemented
    pieces = int(pieces)
    base_units_per_piece = self._granular_units // pieces
    return base_units_per_piece * self.granularity >= self.min_amount


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

    total_units = self._granular_units + other._granular_units
    self._granular_units, other._granular_units = total_units, 0
    return self

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

    total_units = self._granular_units + other._granular_units
    self._granular_units, other._granular_units = 0, total_units
    return other

