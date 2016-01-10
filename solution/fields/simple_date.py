# coding=utf-8
from __future__ import absolute_import
import datetime

from .. import validators as v
from ..utils import Markup, get_html_attrs
from .field import ValidationError
from .text import Text


class SimpleDate(Text):

    """A date field formatted as yyy-MM-dd. Example: 1980-07-28
    This field DOES NOT make any timezone conversions

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value. It must be a `date` or `datetime`.

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
    _type = 'date'
    default_validator = v.IsDate

    def __init__(self, **kwargs):
        kwargs.setdefault('default', None)
        return super(SimpleDate, self).__init__(**kwargs)

    def py_to_str(self, locale=None, **kwargs):
        dt = self.obj_value or self.default
        if not dt:
            return u''
        return dt.isoformat()

    def as_input(self, locale=None, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['type'] = attrs.setdefault('type', self._type)
        attrs['name'] = self.name
        attrs['value'] = self.to_string(**attrs)
        if not self.optional:
            attrs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(attrs)
        return Markup(html)

    def as_textarea(self, locale=None, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs.setdefault('required', True)
        html_attrs = get_html_attrs(attrs)
        value = self.to_string(**attrs)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, value)
        return Markup(html)

    def str_to_py(self, locale=None):
        if not self.str_value:
            return self.default or None
        try:
            dt = [int(f) for f in self.str_value.split('-')]
            return datetime.date(*dt)
        except (ValueError, TypeError):
            raise ValidationError
