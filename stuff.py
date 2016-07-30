"""Contains the Stuff class which represents like bits of arbitrary kinds of stuff."""

class Error(Exception):
  """Top level error for this module."""
  pass

class AmountError(Error):
  """Raised when an invalid amount of stuff is created."""
  pass

class ConfigError(Error):
  """Raised when a Stuff type has an invalid configuration."""
  pass


class MetaStuff(type):
  """Metaclalss for Stuff objects. Handles things like class-level properties and
  registration of Stuff types."""

  @property
  def min_size(self):
    """minimum amount of stuff allowed by this type."""
    return self.__dict__['min_size'].fget(None)

  @property
  def granularity(self):
    """minimum granularity of this type of stuff."""
    return self.__dict__['granularity'].fget(None)

  def __new__(cls, name, bases, namespace, min_size=1, granularity=1):
    _min_size = int(min_size)
    _granularity = int(granularity)

    if _min_size < 1:
      raise ConfigError('min size of stuff must be at least 1')
    if _granularity < 1:
      raise ConfigError('granularity of stuff must be at least 1')

    @property
    def min_size(self):
      return _min_size

    @property
    def granularity(self):
      return _granularity

    namespace['min_size'] = min_size
    namespace['granularity'] = granularity

    return super().__new__(cls, name, bases, namespace)

  def __init__(self, name, bases, namespace, **kwds):
    super().__init__(name, bases, namespace)


class Stuff(object, metaclass=MetaStuff):
  """Keeps track of a kind of stuff based on its type.

  Includes facilities for controlling how granular tracking should be (i.e. what is the
  smallest unit that can be split out). These are controlled by setting keyword arguments to the type constructor.

  :min_size: is the least amount of stuff that an individual object of this type is
    allowed to contain. Defaults to 1.

  :granularity: is the divisibility of objects of this type. When breaking down into
    chunks, objects of this type must contain a multiple of this amount of stuff. Defaults
    to 1.
  """

  def __init__(self, amount=None):
    """Creates new stuff of this type.

    :amount: How much new stuff is created. Will be converted to an integer.
    """
    amount = int(amount)

    if amount % self.granularity != 0:
      raise AmountError('amount is not divisibile by the granularity')
    if amount < self.min_size:
      raise AmountError('amount is less than the minimum size')

    self._granular_units = amount // self.granularity

  @property
  def amount(self):
    """The total amount of stuff contained in this collection."""
    return self._granular_units * self.granularity

  @property
  def smallest_allowed_amount(self):
    """The minimum amount of stuff an instance can contain given the minimum quantity and
    granularity.
    """

  # Implementation of the Data Model for this type.
  def __bool__(self):
    """Returns true if this object contains any stuff."""
    return bool(self.amount)
