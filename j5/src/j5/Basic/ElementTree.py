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

# TODO: check if these are necessary now that the above logic has changed
# Import Extra Things from ElementTree if cElementTree Used

try:
    # Try import extras from default location of ElementTree in Python >= 2.5
    from xml.etree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                      _encode, _escape_attrib, _encode_entity
except ImportError:
    # Try import extras from standalone ElementTree install
    from elementtree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                        _encode, _escape_attrib, _encode_entity

