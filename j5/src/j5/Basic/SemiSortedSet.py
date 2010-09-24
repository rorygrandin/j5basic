#!/usr/bin/env python

import threading
from j5.Basic import Decorators

_base_min = min
_base_max = max

class SemiSortedSet(set):
    """A set that remembers its minimum and maximum, and can do inplace slicing at a certain point in a reasonably optimal way"""
    def __new__(cls, iterable=None):
        self = set.__new__(cls)
        self.lock = threading.RLock()
        if iterable is not None:
            set.__init__(self, iterable)
        else:
            set.__init__(self)
        return self

    @Decorators.SelfLocking.runwithlock
    def copy(self):
        """makes a copy of this SemiSortedSet (with a new lock)"""
        new_self = set.copy(self)
        new_self.lock = threading.RLock()
        return new_self

    @Decorators.SelfLocking.runwithlock
    def min(self):
        """Returns the minimum element in the set"""
        return _base_min(self)

    @Decorators.SelfLocking.runwithlock
    def max(self):
        """Returns the maximum element in the set"""
        return _base_max(self)

    @Decorators.SelfLocking.runwithlock
    def remove_below(self, minimum):
        """Removes all items in the set that are less than the new minimum"""
        items_below = set(item for item in self if item < minimum)
        self.difference_update(items_below)

    @Decorators.SelfLocking.runwithlock
    def remove_above(self, maximum):
        """Removes all items in the set that are greater than the new maximum"""
        items_above = set(item for item in self if item > maximum)
        self.difference_update(items_above)

# Override all inherited methods from set so that they lock safely
method_descriptor = type(set.add)
for function_name in dir(set):
    set_function = getattr(set, function_name)
    if type(set_function) != method_descriptor:
        continue
    override_function = getattr(SemiSortedSet, function_name)
    if override_function is not set_function:
        continue
    new_function = Decorators.SelfLocking.runwithlock(set_function)
    setattr(SemiSortedSet, function_name, new_function)

