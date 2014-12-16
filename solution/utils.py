# coding=utf-8
import re
from xml.sax.saxutils import quoteattr

from markupsafe import Markup, escape_silent
from ._compat import to_unicode, iteritems


class FakeMultiDict(dict):

    """Adds a fake `getlist` method to a regular dict; or acts as a proxy to
    Webob's MultiDict `getall` method.
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as error:
            raise AttributeError(error)

    def getlist(self, name):
        if hasattr(self, 'getall'):
            return self.getall(name)
        value = self.get(name)
        if value is None:
            return []
        return [value]


def escape(value):
    return escape_silent(to_unicode(value))


def get_html_attrs(kwargs=None):
    """Generate HTML attributes from the provided keyword arguments.

    The output value is sorted by the passed keys, to provide consistent
    output.  Because of the frequent use of the normally reserved keyword
    `class`, `classes` is used instead. Also, all underscores are translated
    to regular dashes.

    Set any property with a `True` value.

    >>> _get_html_attrs({'id': 'text1', 'classes': 'myclass',
        'data_id': 1, 'checked': True})
    u'class="myclass" data-id="1" id="text1" checked'

    """
    kwargs = kwargs or {}
    attrs = []
    props = []

    classes = kwargs.get('classes', '').strip()
    if classes:
        classes = ' '.join(re.split(r'\s+', classes))
        classes = to_unicode(quoteattr(classes))
        attrs.append('class=%s' % classes)
    try:
        del kwargs['classes']
    except KeyError:
        pass

    for key, value in iteritems(kwargs):
        key = key.replace('_', '-')
        key = to_unicode(key)
        if isinstance(value, bool):
            if value is True:
                props.append(key)
        else:
            value = quoteattr(Markup(value))
            attrs.append(u'%s=%s' % (key, value))

    attrs.sort()
    props.sort()
    attrs.extend(props)
    return u' '.join(attrs)


def get_obj_value(obj, name, default=None):
    # The field name could conflict with a native method
    # if `obj` is a dictionary instance
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def set_obj_value(obj, name, value):
    # The field name could conflict with a native method
    # if `obj` is a dictionary instance
    if isinstance(obj, dict):
        obj[name] = value
    else:
        setattr(obj, name, value)
