# coding=utf-8
import datetime
import re

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
    rx_time = re.compile(
        '(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2})(:(?P<second>[0-9]{1,2}))?\s?(?P<tt>am|pm)?',
        re.IGNORECASE
    )

    def __init__(self, format='%l:%M %p', **kwargs):
        self.format = format
        kwargs.setdefault('default', None)
        return super(Time, self).__init__(**kwargs)

    def py_to_str(self, format=None, locale=None, **kwargs):
        tt = self.obj_value or self.default
        if not tt:
            return u''
        return tt.strftime(self.format).strip()

    def as_input(self, format=None, locale=None, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['type'] = attrs.setdefault('type', self._type)
        attrs['name'] = self.name
        attrs['value'] = self.to_string(**attrs)
        if not self.optional:
            attrs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(attrs)
        return Markup(html)

    def as_textarea(self, format=None, locale=None, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs.setdefault('required', True)
        html_attrs = get_html_attrs(attrs)
        value = self.to_string(**attrs)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, value)
        return Markup(html)

    def str_to_py(self, format=None, locale=None):
        if not self.str_value:
            return self.default or None
        match = self.rx_time.match(self.str_value.upper())
        if not match:
            raise ValidationError
        try:
            gd = match.groupdict()
            hour = int(gd['hour'])
            minute = int(gd['minute'])
            second = int(gd['second'] or 0)
            if gd['tt'] == 'PM':
                hour += 12
            return datetime.time(hour, minute, second)
        except (ValueError, TypeError):
            raise ValidationError
