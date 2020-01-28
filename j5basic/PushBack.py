#!/usr/bin/env python

"""this is an iterator wrapper that allows things to be pushed back"""

class PushBack(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.pushedback = []

    def __iter__(self):
        return self

    def pushback(self, item):
        self.pushedback.append(item)

    def next(self):
        if self.pushedback:
            return self.pushedback.pop(0)
        else:
            return self.iterator.next()

class PushToBack(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.pushedtoback = []
        self.iterator_done = False

    def __iter__(self):
        return self

    def pushback(self, item):
        self.pushedtoback.append(item)

    def next(self):
        if not self.iterator_done:
            try:
                return self.iterator.next()
            except StopIteration:
                self.iterator_done = True
        if len(self.pushedtoback):
            return self.pushedtoback.pop(0)
        raise StopIteration()

