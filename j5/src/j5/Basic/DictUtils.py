#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implements a case-insensitive (on keys) dictionary and various dictionary functions"""

# Copyright 2002, 2003 St James Software

from j5.Config import ConfigTree

def assert_dicts_equal(dict1,dict2):
    """tests equality of two dicts"""
    k1, k2 = dict1.keys(), dict2.keys()
    k1.sort()
    k2.sort()

    assert k1 == k2
    for key in k1:
        # this assert means we get the key if the assert fails
        assert (dict1[key], key) == (dict2[key], key)

def assert_dicts_not_equal(dict1,dict2):
    """tests two dicts are not equal"""
    k1, k2 = dict1.keys(), dict2.keys()
    k1.sort()
    k2.sort()

    if k1 == k2:
        for key in k1:
            if (dict1[key], key) != (dict2[key], key):
                return
        assert False, (k1, k2)

def filterdict(origdict, keyset):
    """returns the subset of origdict containing only the keys in keyset and their corresponding values """
    newdict = {}
    # this cunningly works with cidict (case-insensitive dictionary class)
    # since we just check if key in origdict, not the reverse...
    # the keys are those from keyset, not origdict
    for key in keyset:
        if key in origdict:
            newdict[key] = origdict[key]
    return newdict

def subtractdicts(ldict, rdict):
    """returns a dictionary containing those keys&values in ldict that aren't in rdict or differ from rdict"""
    diffdict = {}
    for key in ldict:
        if key in rdict:
            lvalue, rvalue = ldict[key], rdict[key]
            # type mismatch doesn't count if both are str/unicode
            if (type(lvalue) != type(rvalue)) and not (type(lvalue) in (str, unicode) and type(rvalue) in (str, unicode)):
                diffdict[key] = lvalue
            elif type(lvalue) != type(rvalue):
                # handle str/unicode mismatch
                if type(lvalue) == str: lvaluecmp = lvalue.decode('UTF-8')
                else: lvaluecmp = lvalue
                if type(rvalue) == str: rvaluecmp = rvalue.decode('UTF-8')
                else: rvaluecmp = rvalue
                if lvaluecmp != rvaluecmp:
                    diffdict[key] = lvalue
            elif lvalue != rvalue:
                diffdict[key] = lvalue
        else:
            diffdict[key] = ldict[key]
    return diffdict

def mapdict(thedict, keymap, valuemap):
    """ returns a dictionary with the keys mapped using keymap, the values using valuemap """
    if keymap is None:
        if valuemap is None:
            return thedict
        else:
            return dict([(key, valuemap(value)) for key, value in thedict.iteritems()])
    else:
        if valuemap is None:
            return dict([(keymap(key), value) for key, value in thedict.iteritems()])
        else:
            return dict([(keymap(key), valuemap(value)) for key, value in thedict.iteritems()])

def generalupper(str):
    """this uses the object's upper method - works with string and unicode"""
    if str is None: return str
    return str.upper()

def upperkeys(thedict):
    return mapdict(thedict, generalupper, None)

class cidict(dict):
    def __init__(self, fromdict = None):
        """constructs the cidict, optionally using another dict to do so"""
        if fromdict is not None:
            self.update(fromdict)

    def __getitem__(self, key):
        if type(key) != str and type(key) != unicode:
            raise TypeError, "cidict can only have str or unicode as key (got %r)" % type(key)
        for akey in self.iterkeys():
            if akey.lower() == key.lower():
                return dict.__getitem__(self, akey)
        raise IndexError

    def __setitem__(self, key, value):
        if type(key) != str and type(key) != unicode:
            raise TypeError, "cidict can only have str or unicode as key (got %r)" % type(key)
        for akey in self.iterkeys():
            if akey.lower() == key.lower():
                return dict.__setitem__(self, akey, value)
        return dict.__setitem__(self, key, value)

    def update(self, updatedict):
        """D.update(E) -> None.  Update D from E: for k in E.keys(): D[k] = E[k]"""
        for key, value in updatedict.iteritems():
            self[key] = value

    def __delitem__(self, key):
        if type(key) != str and type(key) != unicode:
            raise TypeError, "cidict can only have str or unicode as key (got %r)" % type(key)
        for akey in self.iterkeys():
            if akey.lower() == key.lower():
                return dict.__delitem__(self, akey)
        raise IndexError

    def __contains__(self, key):
        if type(key) != str and type(key) != unicode:
            raise TypeError, "cidict can only have str or unicode as key (got %r)" % type(key)
        for akey in self.iterkeys():
            if akey.lower() == key.lower():
                return 1
        return 0

    def has_key(self, key):
        return self.__contains__(key)

    def get(self, key, default=None):
        if self.has_key(key):
            return self[key]
        else:
            return default

class ordereddict(dict):
    """a dictionary which remembers its keys in the order in which they were given"""
    def __init__(self, *args):
        if len(args) == 0:
            super(ordereddict, self).__init__()
            self.order = []
        elif len(args) > 1:
            raise TypeError("ordereddict() takes at most 1 argument (%d given)" % len(args))
        else:
            initarg = args[0]
            apply(super(ordereddict, self).__init__, args)
            if hasattr(initarg, "keys"):
                self.order = initarg.keys()
            else:
                # danger: could have duplicate keys...
                self.order = []
                checkduplicates = {}
                for key, value in initarg:
                    if not key in checkduplicates:
                        self.order.append(key)
                        checkduplicates[key] = None

    def __setitem__(self, key, value):
        alreadypresent = key in self
        result = dict.__setitem__(self, key, value)
        if not alreadypresent: self.order.append(key)
        return result

    def setdefault(self, key, default):
        """D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D"""
        if key in self:
            return self[key]
        else:
            self[key] = default
            return self[key]

    def update(self, updatedict):
        """D.update(E) -> None.  Update D from E: for k in E.keys(): D[k] = E[k]"""
        for key, value in updatedict.iteritems():
            self[key] = value

    def __delitem__(self, key):
        alreadypresent = key in self
        result = dict.__delitem__(self, key)
        if not alreadypresent: del self.order[self.order.find(key)]
        return result

    def copy(self):
        """D.copy() -> a shallow copy of D"""
        thecopy = ordereddict(super(ordereddict, self).copy())
        thecopy.order = self.order[:]
        return thecopy

    def items(self):
        """D.items() -> list of D's (key, value) pairs, as 2-tuples"""
        return [(key, self[key]) for key in self.order]

    def iteritems(self):
        """D.iteritems() -> an iterator over the (key, value) items of D"""
        for key in self.order:
            yield (key, self[key])

    def iterkeys(self):
        """D.iterkeys() -> an iterator over the keys of D"""
        for key in self.order:
            yield key

    __iter__ = iterkeys

    def itervalues(self):
        """D.itervalues() -> an iterator over the values of D"""
        for key in self.order:
            yield self[key]

    def keys(self):
        """D.keys() -> list of D's keys"""
        return self.order[:]

    def values(self):
        """D.values() -> lif of D's values (in the same order as D.keys())"""
        return [self[key] for key in self.order]

    def popitem(self):
        """D.popitem() -> (k, v), remove and return some (key, value) pair as a 2-tuple; but raise KeyError if D is empty"""
        if len(self.order) == 0:
            raise KeyError("popitem(): ordered dictionary is empty")
        k = self.order.pop()
        v = self[k]
        del self[k]
        return (k,v)


class attrdict(dict):
    """Dictionary that also allows access to keys using attributes"""
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            return None

def attribify(context):
    """takes a set of nested dictionaries and converts them into attrdicts. Also searches through lists"""
    # We shouldn't convert Config nodes
    if isinstance(context, dict) and not isinstance(context, attrdict) and not isinstance(context, ConfigTree.Node):
        newcontext = attrdict(context)
        for key, value in newcontext.items():
            if isinstance(value, (dict, list)):
                newcontext[key] = attribify(value)
        return newcontext
    elif isinstance(context, list):
        for n, item in enumerate(context):
            if isinstance(item, (dict, list)):
                context[n] = attribify(item)
        return context
    else:
        return context

