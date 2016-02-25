# coding=utf-8
from __future__ import absolute_import
import datetime

import pytz

from .. import validators as v
from .._compat import string_types
from ..utils import Markup, get_html_attrs

from .field import ValidationError
from .text import Text


class Date(Text):

    """A datetime field formatted as yyyy-MM-dd. Example: 1980-07-28
    If the form or this field has a tz parameter, the value will be rendered with
    that timezone and converted back when saving, so the python value will be always
    a ``datetime.datetime``

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value. It must be a `datetime`.

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

    :param tz:
        Default timezone for this field.

    """
    _type = 'date'
    default_validator = v.IsDate

    def __init__(self, **kwargs):
        kwargs.setdefault('default', None)
        return super(Date, self).__init__(**kwargs)

    def _get_tz(self):
        tz = self.tz or pytz.utc
        if tz and isinstance(tz, string_types):
            tz = pytz.timezone(tz)
        self.tz = tz
        return tz

    def _to_timezone(self, dt):
        """Takes a naive timezone with an utc value and return it formatted as a
        local timezone."""
        tz = self._get_tz()
        utc_dt = pytz.utc.localize(dt)
        return utc_dt.astimezone(tz)

    def _to_utc(self, dt):
        """Takes a naive timezone with an localized value and return it formatted
        as utc."""
        tz = self._get_tz()
        loc_dt = tz.localize(dt)
        return loc_dt.astimezone(pytz.utc)

    def py_to_str(self, **kwargs):
        dt = self.obj_value or self.default
        if not dt:
            return u''
        dt = self._to_timezone(dt)
        return '{dt.year}-{dt.month:02d}-{dt.day:02d}'.format(dt=dt)

    def as_input(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['type'] = attrs.setdefault('type', self._type)
        attrs['name'] = self.name
        attrs['value'] = self.to_string(**attrs)
        if not self.optional:
            attrs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(attrs)
        return Markup(html)

    def as_textarea(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs.setdefault('required', True)
        html_attrs = get_html_attrs(attrs)
        value = self.to_string(**attrs)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, value)
        return Markup(html)

    def str_to_py(self, **kwargs):
        if not self.str_value:
            return self.default or None
        try:
            ldt = [int(f) for f in self.str_value.split('-')]
            dt = datetime.datetime(*ldt)
        except (ValueError, TypeError):
            raise ValidationError
        dt = self._to_utc(dt)
        return dt.replace(tzinfo=None)
