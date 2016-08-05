from abc import ABCMeta, abstractmethod

from stuff.stuff import Stuff, MetaStuff

__all__ = ['ISized', 'MetaUniqueStuff', 'UniqueStuff']


class ISized(metaclass=ABCMeta):
  """An abstract class for types of unique stuff which should have unique sizes per item.
  """
  @abstractmethod
  def __stuff_size__(self):
    """The size of this item of unique stuff."""
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

  :min_units: is the least number of units of stuff that an individual object of this type
    is allowed to contain. Defaults to 1. (Objects are always allowed to contain zero
    stuff, no matter the set minimum. The minimum applies to any nonzero amount of stuff).

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
  def min_size(cls):
    """The minimum nonzero size of stuff an instance can contain given the minimum
    quantity and unit_size.

    Always returns zero if unit_type inherits from ISized.
    """
    if cls.unit_type is not None:
      return 0.0
    else:
      return super().min_size()

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
