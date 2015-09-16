# coding=utf-8
from __future__ import absolute_import

from ..utils import Markup, get_html_attrs
from .field import Field


FALSY_VALUES = [u'', u'0', u'no', u'off', u'false']


class Boolean(Field):
    """A True/False field.

    :param falsy:
        A list of raw values considered `False`.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that takes the current value as a string
        and preprocess it before rendering.

    :param clean:
        An optional function that takes the value already converted to
        python and return a 'cleaned' version of it. If the value can't be
        cleaned `None` must be returned instead.

    :param hide_value:
        Do not render the current value a a string. Useful with passwords
        fields.

    """

    def __init__(self, falsy=FALSY_VALUES, **kwargs):
        kwargs.setdefault('default', False)
        self.falsy = falsy
        super(Boolean, self).__init__(**kwargs)

    def py_to_str(self, **kwargs):
        return u'1' if self.obj_value else u''

    def str_to_py(self, **kwargs):
        if not self.str_value or (self.str_value.lower() in self.falsy):
            return False
        return True

    def is_empty(self, py_value):
        return False

    def __call__(self, **kwargs):
        return self.as_checkbox(**kwargs)

    def as_checkbox(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs.setdefault('type', 'checkbox')
        attrs['name'] = self.name
        value = self.to_string(**attrs)
        is_true = value and (value.lower() not in self.falsy)
        if is_true and attrs['type'] == 'checkbox':
            attrs['checked'] = True
        if not self.optional:
            attrs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(attrs)
        return Markup(html)
