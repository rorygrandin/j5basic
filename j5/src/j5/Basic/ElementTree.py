"""Wrapper for importing any of the various ElementTree implementations."""

SomeElementTreeImported = False

# Import Basic ElementTree

if not SomeElementTreeImported:
    try:
        # default location of cElementTree on Python >= 2.5
        from xml.etree.cElementTree import *
        SomeElementTreeImported = True
    except ImportError:
        pass
    try:
        # default location of ElementTree on Python >= 2.5
        from xml.etree.ElementTree import *
        SomeElementTreeImported = True
    except ImportError:
        pass

if not SomeElementTreeImported:
    # last ditch attempt at import
    # try standalone ElementTree install
    from elementtree.ElementTree import *
    SomeElementTreeImported = True
    try:
        # try standalone cElementTree install
        from cElementTree import *
        SomeElementTreeImported = True
    except ImportError:
        pass

# Import Extra Things from ElementTree that are private elements we need from outside

try:
    # Try import extras from default location of ElementTree in Python 2.5-2.6
    from xml.etree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                      _encode, _escape_attrib, _encode_entity
except ImportError:
    # Try import extras from default location of ElementTree in Python >=2.7
    try:
        from xml.etree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                          _encode, _escape_attrib
        def _encode_entity(data, pattern):
            return _encode(data)
    except ImportError:
        # Try import extras from standalone ElementTree install
        from elementtree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                        _encode, _escape_attrib, _encode_entity

