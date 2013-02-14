import copy
import xml
from lxml.html import clean
from lxml.html import tostring, fromstring

class Cleaner(clean.Cleaner):
    def clean_html(self, html):
        if not html:
            return html
        if not html.strip():
            return html
        if not isinstance(html, basestring):
            raise ValueError('We only support cleaning HTML fragments')
        encode = False
        if not isinstance(html, unicode):
            html = html.decode('utf-8')
            encode = True

        #We wrap the content up in an extra div tag (otherwise lxml does wierd things to it - like adding in <p> tags and stuff)
        divnode = fromstring(u'<div>' + html + u'</div>')
        self(divnode)
        #Now unwrap it (i.e. just serialize the children of our extra div node:
        cleaned = xml.sax.saxutils.escape(divnode.text) if divnode.text else ''
        for n in divnode:
            cleaned += tostring(n, encoding = unicode, method = 'xml')
        if encode:
            cleaned = cleaned.encode('utf-8')
        return cleaned

cleaner = Cleaner()
clean_html = cleaner.clean_html
