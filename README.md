# Stuff!

Contains classes for keeping track of ammounts of arbitrary kinds of stuff, with type
safety.

Typical usage is by defining a new type of stuff by subclassing Stuff.

Operations involving stuff conserve stuff, so the only way to get more of a particular
kind of stuff is through the type's constructor.

    >>> from stuff import *
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

Custom types of stuff may also contain their own unique properties for whatever else you
want to store on them. This can also be useful to create conversions between kinds of
stuff.

Possible future additions (no plans for development):

- UniqueStuff: track individual objects, by holding a set rather than just a counter.
  Seems pretty easy, as long as you don't care which objects end up in which blob when you
  divid a stuff into multiple smaller stuff.
- Stuff Categories: Some way of grouping together more than one type of stuff as a mass
  blob that can be treated as one type of stuff for some purposes but still retains
  information on what kinds of more specific stuff are in it. For example grouping
  together Energy and DarkEnergy in a category that can be handled by an energy relay
  while still knowing that they are distinct. Not sure if this would be doable in a way
  that was useful at all.
