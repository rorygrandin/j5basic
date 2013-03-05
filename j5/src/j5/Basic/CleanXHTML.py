import copy
import cssutils
from xml.sax import saxutils
from lxml.html import tostring, fromstring, clean
from lxml import etree

class Cleaner(clean.Cleaner):
    def clean_html(self, html):
        if not isinstance(html, unicode):
            raise ValueError('We only support cleaning unicode HTML fragments')

        #We wrap the content up in an extra div tag (otherwise lxml does wierd things to it - like adding in <p> tags and stuff)
        divnode = fromstring(u'<div>' + html + u'</div>')
        self(divnode)
        #Now unwrap it (i.e. just serialize the children of our extra div node:
        cleaned = saxutils.escape(divnode.text) if divnode.text else ''
        for n in divnode:
            cleaned += tostring(n, encoding = unicode, method = 'xml')
        return cleaned

def clean_tags(html):
    """clean assumes you tidied first..."""
    root = etree.fromstring("<div>" + html + "</div>")
    for cls in etree.XPath("//@class")(root):
        parent = cls.getparent()
        classes = [cls for cls in cls.split() if not cls.lower().startswith("mso")]
        if not classes:
            parent.attrib.pop("class", None)
        else:
            parent.attrib["class"] = " ".join(classes)
    for c in root.xpath('//comment()'):
        p = c.getparent()
        p.remove(c)
    for style in etree.XPath("//@style")(root):
        parent = style.getparent()
        cssStyle = cssutils.parseStyle(style)

        #Strip all style elements that originate from MS
        for key in cssStyle.keys():
            if key.startswith('mso'):
                del cssStyle[key]

        new_style = cssStyle.cssText
        if not new_style.strip():
            parent.attrib.pop("style", None)
        else:
            parent.attrib["style"] = new_style

    #Now unwrap it (i.e. just serialize the children of our extra div node:
    cleaned = saxutils.escape(root.text) if root.text else ''

    for n in root:
        cleaned += etree.tostring(n, encoding = unicode, method = 'xml')

    return cleaned

cleaner = Cleaner()
clean_html = cleaner.clean_html
