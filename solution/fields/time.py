# -*- coding: utf-8 -*-
import datetime

from .. import validators as v
from ..utils import Markup, get_html_attrs
from .field import ValidationError
from .text import Text


class Time(Text):

    """A time field formatted as 'HH:mm AA'. Examples: 5:03 AM, 11:00 PM
    This field DOES NOT make any timezone conversions

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value. It must be a `datetime.time`.

    :param prepare:
        An optional function that takes the current value as a string
        and preprocess it before rendering.

    :param clean:
        An optional function that takes the value already converted to
        python and return a 'cleaned' version of it. If the value can't be
        cleaned `None` must be returned instead.

    :param hide_value:
        Do not render the current value a a string.

    """
    _type = 'time'
    default_validator = v.IsTime

    def __init__(self, **kwargs):
        kwargs.setdefault('default', None)
        return super(Time, self).__init__(**kwargs)

    def py_to_str(self, format=None, locale=None, **kwargs):
        tt = self.obj_value or self.default
        if not tt:
            return u''
        return tt.strftime('%l:%M %p').strip()

    def as_input(self, format=None, locale=None, **kwargs):
        kwargs['type'] = kwargs.setdefault('type', self._type)
        kwargs['name'] = self.name
        kwargs['value'] = self.to_string(**kwargs)
        if not self.optional:
            kwargs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(kwargs)
        return Markup(html)

    def as_textarea(self, format=None, locale=None, **kwargs):
        kwargs['name'] = self.name
        if not self.optional:
            kwargs.setdefault('required', True)
        html_attrs = get_html_attrs(kwargs)
        value = self.to_string(**kwargs)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, value)
        return Markup(html)

    def str_to_py(self, format=None, locale=None):
        if not self.str_value:
            return self.default or None
        try:
            num, p = self.str_value.upper().split(' ')
            splitted = [int(n) for n in num.split(':')]
            splitted.append(0)
            hour = splitted[0]
            minute = splitted[1]
            second = splitted[2]
            if p == 'PM':
                hour = hour + 12
            return datetime.time(hour, minute, second)
        except (ValueError, TypeError):
            raise ValidationError
