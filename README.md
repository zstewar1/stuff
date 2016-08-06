# Stuff!

Contains classes for keeping track of ammounts of arbitrary kinds of stuff, with type
safety.

Typical usage is by defining a new type of stuff by subclassing Stuff.

Operations involving stuff conserve stuff, so the only way to get more of a particular
kind of stuff is through the type's constructor or by explicitly adding it.

    >>> from stuff import *
    >>> class MyStuff(Stuff):
    ...   unit_size = 2.5
    ...   name = 'my stuff'

This creates a kind of stuff called MyStuff which can only be constructed in blobs of
three at a time, and requires at least 6 items for any nonempty instance.

Instance of MyStuff can be created, and stuff can be moved between them:

    >>> x = MyStuff(9) # create 9 new stuff
    >>> y = MyStuff(18) # create 18 new stuff

    >>> (y - 6) >> x # Remove 6 stuff from y, and send it to x.
    [15 of my stuff]
    >>> y
    [12 of my stuff]
    >>> x
    [15 of my stuff]

Supported operations include:
  - Addition: combine two stuff into a new stuff, emptying the originals in the process.
  - In-Place Addition: put all the stuff from one stuff into another stuff.
  - Subtraction: split off some amount of stuff into a new object.
  - Division: split stuff into a tuple of smaller bits of stuff.
  - Left Shift: Put all the stuff in the left operand.
  - Right Shift: Put all the stuff in the right operand.

Stuff is type safe, so every new stuff subtype cannot be mixed with any other type of
stuff.

Custom types of stuff may also contain their own unique properties for whatever else you
want to store on them. This can also be useful to create conversions between kinds of
stuff.

## Properties of Stuff

- Units: Stuff is tracked as units. The operations on stuff usually work in terms of the
  underlying units. Different types of stuff use different unit types.

- Size: this measures how much stuff something has. The library doesn't currently make use
  of size for tracking, but does calculate it. Future versions may use size to create
  `Container` types which have limits on how much stuff they can hold.

## Types of Stuff

- `Stuff`: The base type uses integers for its units. When adding, removing, or separating
  stuff, the number of units must be an integer. Base stuff types are useful for tracking
  numbers of whole objects where the objects don't have unique identities. For example,
  tracking amunition in a game could use a subclass of `Stuff` for each distinct type of
  amunition because each projectile is a whole unit, but individula pieces of amunition
  don't need to be tracked as objects.

- `RealStuff`: Real stuff uses floating point (reals) for its units. RealStuff is assumed
  to be infinitely divisible (within floating point error). If there is a limit to how
  divisible yor stuff is, you should use `Stuff` with a small `unit_size`. `RealStuff` is
  useful for tracking amounts of things like fluids, gasses, or energy.

- `UniqueStuff`: Tracks unique objects. For this purpose the backing type is a `set`.
  Unique stuff can also set a type of objects contained, in which case the `UniqueStuff`
  will reject objects of the wrong type. All of the items in a UniqueStuff are assumed to
  be identical in size (with size `unit_size`) unless the `unit_type` is a subclass of
  `ISized`. If `unit_type` is a subclass of `ISized`, the size of the `UniqueStuff` is the
  sum of the sizes of its contents.

## Future Plans

These additions are the next development priorities:

- `CategoricStuff`: Tracks stuff of other types of stuff, including other categories. The
  units of `CategoricStuff` are dictionaries of stuff-types to a single stuff object
  containing stuff of that type. The size of a category object is the sum of the sizes of
  its contents. Categories additional allow providing a `set` of allowed types of
  contents, in which case attempting to add subtypes not in the provided set will fail.

  Open Design Problems:

  - How to handle failures when adding or subtracting part of a dictionary? When combing,
    or separating stuff from a dictionary of content types, it is possible that one or
    more of the subtype content additions will fail. We have to decide what state that
    should leave the category and all preceeding (and following) stuff types in. For
    example, consider the following:

    Suppose that the category has contents like this:

        {
          StuffTypeA: [8 StuffTypeA],
          StuffTypeB: [3 StuffTypeB],
          StuffTypeC: [6 StuffTypeC],
        }

    And then suppose that we attempt to separate this stuff from this category:

        {
          StuffTypeA: 4,
          StuffTypeB: 7,
          StuffTypeC: 2,
        }

    For this purpose, suppose that the separations are performed in the order they appear
    in the dict. Then first, 4 stuff is removed from the `StuffTypeA` category, creating a
    new object containing 4 of type a, and leaving behind 4 type a. But then the removal
    from `StuffTypeB` fails. If this error is allowed to propagate, then the four
    separated stuff of type a will not be returned and will be discarded.

    There are some options for dealing with this:

    1. Roll back after an error. The category can keep track of separated/added stuff and
       put it back after a failure. This has a small chance of causing an additional
       error, but only if the stuff subtypes override operations unsafely, in which case,
       it probably *should* be an error at that point anyway.

    2. Continue after an error. Mark the failed type as failed, and continue with the
       remaining types. The returned value would have something to indicate that it
       failed, but the rest would be changed and returned normally. The semantics of this
       are more complicated for some operations, and this will make using the result
       harder.

    3. Add a check operation for each operation, which will return a boolean as to whether
       the associated operation would succeed. Like option 1 above, this will fail if
       subtypes override the operation unsafely, but unlike option 1 this will require a
       lot of additional code in the existing types.

    Doing a roll back is probably the best option, at this point.

- `Container`: Holds up to a maximum (and possibly minimum) amount of stuff. A container
  would hold a bounded amount of stuff, potentially bounded on either number of units or
  size. (Units would be easier for Real or Integral valued stuff, but Size would be more
  meaningful for UniqueStuff or CategoricStuff). Containers would not themselves be
  `Stuff`, however each Container subclass would automatically generate an associated
  subtype of `UniqueStuff` which would hold only that `Container` type. Containers would
  be ISized, but the size limit applied to the contents would be distinct from the size of
  the container. This would allow using continers to bridge between sizes of incompatible
  hypothetical units, e.g. the "size" of a quantity of Energy is not meaningful as a size
  quantity for Cargo.

  The combination of `UniqueStuff`, `Containers`, and `CategoricStuff` would create a
  variety of ways to keep track of quantities of things, for example:

  - Have `Air`, `Energy`, and `Coolant` be subtypes of `RealStuff`, since they are
    effectively infinitely divisible.

  - Have `Missiles` (or a few different types of missiles) and such be `Stuff`, since they
    are whole objects but not unique objects.

  - Have `ScientificCargo` be `UniqueStuff`, since it is cargo that has to be brought to a
    particular location, even if you have a bunch of it, you still need to track each
    piece individually.

  - Have `PressureTanks` which hold arbitrarily large quantities of `Air`, but have a
    fixed size. This type could then calculate a `pressure` from the contained quantity vs
    the size.

  - Other container types for `Energy` and `Coolante`

  - Some of these could be composed into a `SmallCargo` category, which is used to fill a
    `Crate` container, which is part of the `Cargo` category, which fills the `Hold`
    container.

  Open Design Problems:

  - Should all containers also be distinct types, or would they better be done as one type
    with some informational tags?

  - How to enforce size limits? Current API doesn't easily supply actual size (since
    subtypes can redefine their `size` based on their contents) without actually doing the
    addition.

    Options:

    - Apply and roll back. Add the stuff and then if the size is too large or too small,
      roll back the change. This should work for most stuff as long as the contract of
      'add/remove', 'put/separate' must be inverses are observed.

    - Require stuff to supply additional methods for checking its future size.

- Support for `UniqueStuff.separate` to take a predicate to choose what to separate. The
  current implementation requires accessing the contents first, and building a set of
  things to separate, then passing that to separate. This would allow passing a predicate
  which receives a thing and returns a boolean of whether it should be separatedt.
