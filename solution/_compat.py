# coding=utf-8
"""
Utilities for writing code that runs on Python 2 and 3.
"""
import sys


PY2 = sys.version_info[0] == 2


if PY2:
    from urlparse import urlsplit, urlunsplit

    text_type = unicode
    string_types = (basestring, )

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls
else:
    from urllib.parse import urlsplit, urlunsplit

    text_type = str
    string_types = (str, )
    implements_to_string = lambda x: x


def to_unicode(x, charset='utf-8', errors='strict',
               allow_none_charset=False):
    if x is None:
        return None
    if not isinstance(x, bytes):
        return text_type(x)
    if charset is None and allow_none_charset:
        return x
    return x.decode(charset, errors)


def iteritems(d, **kw):
    """Return an iterator over the (key, value) pairs of a dictionary."""
    if not PY2:
        return iter(d.items(**kw))
    return d.iteritems(**kw)


def itervalues(d, **kw):
    """Return an iterator over the values of a dictionary."""
    if not PY2:
        return iter(d.values(**kw))
    return d.itervalues(**kw)
