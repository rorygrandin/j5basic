"""Wrapper for importing any of the various ElementTree implementations."""

SomeElementTreeImported = False

import sys
import logging

try:
    from lxml import etree
except ImportError:
    from xml import etree
# Import Basic ElementTree

try:
    # default location of cElementTree on Python >= 2.5
    from xml.etree.cElementTree import *
    SomeElementTreeImported = True
except ImportError:
    pass
if not SomeElementTreeImported:
    # After cElementTree, lxml.etree is the fastest
    try:
        from lxml.etree import *
        SomeElementTreeImported = True
    except ImportError:
        pass
if not SomeElementTreeImported:
    from xml.etree.ElementTree import *
    SomeElementTreeImported = True

if "PyPy" in sys.version:
    logging.warn("Using PyPy-specific monkey-patching of etree")
    import lxml
    sys.modules["lxml.etree"] = lxml.etree = sys.modules["xml.etree.ElementTree"]
    orig_tostring = tostring
    def lxml_tostring(element, encoding=None, method=None, xml_declaration=True, pretty_print=False):
        if 'nsmap' in element.attrib:
            for k, v in sorted(element.attrib.pop('nsmap').items()):
                element.attrib['xmlns:%s' % k] = v
        return orig_tostring(element, encoding, method)
    lxml.etree.tostring = lxml_tostring

# Import Extra Things from ElementTree that are private elements we need from outside

try:
    # Try import extras from default location of ElementTree in Python 2.5-2.6
    from xml.etree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                      _encode, _escape_attrib, _encode_entity
except ImportError:
    # Try import extras from default location of ElementTree in Python >=2.7
    try:
        import string
        from xml.etree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                          _encode, _escape_attrib
        _escape_map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
        }
        def _encode_entity(text, pattern):
            def escape_entities(m, map=_escape_map):
                out = []
                append = out.append
                for char in m.group():
                    text = map.get(char)
                    if text is None:
                        text = "&#%d;" % ord(char)
                    append(text)
                return string.join(out, "")
            try:
                return _encode(pattern.sub(escape_entities, text), "utf-8")
            except TypeError:
                _raise_serialization_error(text)
    except ImportError:
        # Try import extras from standalone ElementTree install
        from elementtree.ElementTree import _escape_cdata, _raise_serialization_error, \
                                        _encode, _escape_attrib, _encode_entity


# Fast parsing from lxml
# infile is a file object to be processed
# events is a tuple of a selection of events of interest (start, end, data, close)
# tag is the tagname of interest (e.g. AttributeType)
# func gets passed each event, element tuple in a context to process
# As this clears the memory after processing each element, it avoids high memory usage
def fast_iter(func, infile, events=('end',), tag=None):
    context = etree.iterparse(infile, events=events, tag=tag)
    for event, elem in context:
        func(event, elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context

