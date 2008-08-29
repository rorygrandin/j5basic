# -*- coding: utf-8 -*-
#
# Some of this is originally from trac/core.py
# The original header is included below
# The licensing terms are modified BSD (without the advertising clause)
#################
# Copyright (C) 2003-2008 Edgewall Software
# Copyright (C) 2003-2004 Jonas Borgström <jonas@edgewall.com>
# Copyright (C) 2004-2005 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Jonas Borgström <jonas@edgewall.com>
#         Christopher Lenz <cmlenz@gmx.de>

class APIError(Exception):
    """Exception base class for errors with APIs."""
    pass

class API(object):
    """Marker base class for implementable (but not neccesarily singleton component-based) APIs"""


class APIMeta(type):
    """Meta class for objects that implement an API.
    """

    def __new__(cls, name, bases, d):
        """Create the class."""

        new_class = type.__new__(cls, name, bases, d)

        if d.get('abstract'):
            # Don't put abstract component classes in the registry
            return new_class

        check_interfaces = []
        for interface in d.get('_implements', []):
            check_interfaces.append(interface)
        for base in [base for base in bases if hasattr(base, '_implements')]:
            for interface in base._implements:
                check_interfaces.append(interface)

        for interface in check_interfaces:
            for method in dir(interface):
                if not hasattr(new_class, method):
                    raise APIError("Class %s does not implement method %s from API %s" % (new_class, method, interface))
        return new_class

def supports(cls, *interfaces):
    """Can be used to query whether a particular class supports the given API"""
    if not hasattr(cls, "_implements"):
        return False
    for interface in interfaces:
        if not interface in cls._implements:
            return False
    return True

def implements(*interfaces):
    """Can be used in the class definiton of `Component` subclasses to
    declare the extension points that are extended.
    Can also be used for normal classes to declare them implementing
    `API`s.
    """
    import sys

    frame = sys._getframe(1)
    locals_ = frame.f_locals

    # Some sanity checks
    assert locals_ is not frame.f_globals and '__module__' in locals_, \
           'implements() can only be used in a class definition'

    locals_.setdefault('_implements', []).extend(interfaces)

