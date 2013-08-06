# -*- coding: utf-8 -*-
"""
Utilities for writing code that runs on Python 2 and 3.
"""
import sys


PY2 = sys.version_info[0] == 2


if PY2:
    string_types = (basestring, )

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls
else:
    string_types = (str, )
    implements_to_string = lambda x: x


def to_unicode(txt, encoding='utf8'):
    if not isinstance(txt, string_types):
        txt = repr(txt)
    if not PY2:
        return str(txt)
    if isinstance(txt, unicode):
        return txt
    return unicode(txt, encoding)


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
