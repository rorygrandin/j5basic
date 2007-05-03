"""Wrapper for importing any of the various ElementTree implementations."""

ElementTreeImported = False

if not ElementTreeImported:
    try:
        # default location of cElementTree on Python >= 2.5
        from xml.etree.cElementTree import *
        ElementTreeImported = True
    except ImportError:
        pass

if not ElementTreeImported:
    try:
        # default location of ElementTree on Python >= 2.5
        from xml.etree.ElementTree import *
        ElementTreeImported = True
    except ImportError:
        pass

if not ElementTreeImported:
    try:
        # try standalone cElementTree install
        from cElementTree import *
        ElementTreeImported = True
    except ImportError:
        pass

if not ElementTreeImported:
    # last ditch attempt at import
    # try standalone ElementTree install
    from elementtree import *
    ElementTreeImported = True


