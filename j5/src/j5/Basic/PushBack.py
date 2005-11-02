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

