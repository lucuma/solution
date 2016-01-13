# coding=utf-8
from __future__ import absolute_import
import datetime
import re

import pytz

from .. import validators as v
from .._compat import string_types
from ..utils import Markup, get_html_attrs

from .field import ValidationError
from .field import Field


class SplittedDateTime(Field):

    """A field rendered as two separated <input>, but stored as a single
    ``datetime`` object.

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
    default_validator = v.IsDate
    rx_time = re.compile(
        '(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2})(:(?P<second>[0-9]{1,2}))?\s?(?P<tt>am|pm)?',
        re.IGNORECASE
    )

    def __init__(self, time_format='%l:%M %p', **kwargs):
        kwargs.setdefault('default', [])
        self.time_format = time_format
        return super(SplittedDateTime, self).__init__(**kwargs)

    def _get_tz(self):
        tz = self.tz or pytz.utc
        if tz and isinstance(tz, string_types):
            tz = pytz.timezone(tz)
        self.tz = tz
        return tz

    def _clean_data(self, str_value, file_data, obj_value):
        """This overwrite is neccesary for work with multivalues"""
        str_value = str_value or None
        obj_value = obj_value or None
        return (str_value, None, obj_value)

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

    def _str_to_datetime(self, str_value):
        """Parses a `YYYY-MM-DD` string into a datetime object."""
        try:
            ldt = [int(f) for f in str_value.split('-')]
            dt = datetime.datetime(*ldt)
        except (ValueError, TypeError):
            return None
        return dt

    def _str_to_time(self, str_value):
        """Parses a `hh:mm` or a `hh:mm pm` string into a time object."""
        match = self.rx_time.match(str_value.upper())
        if not match:
            return None
        try:
            gd = match.groupdict()
            hour = int(gd['hour'])
            minute = int(gd['minute'])
            second = int(gd['second'] or 0)
            if gd['tt'] == 'PM':
                hour += 12
            return datetime.time(hour, minute, second)
        except (ValueError, TypeError):
            return None

    def py_to_str(self, **kwargs):
        dt = self.obj_value or self.default
        if not dt:
            return None
        ldt = self._to_timezone(dt)
        return ldt

    def as_inputs(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs.setdefault('required', True)
        _forced_type = attrs.get('type')

        str_dt = str_tt = ''
        ldt = self.to_string(**attrs)
        if ldt:
            if isinstance(ldt, list):
                str_dt, str_tt = ldt
            else:
                str_dt = '{dt.year}-{dt.month:02d}-{dt.day:02d}'.format(dt=ldt.date())
                str_tt = ldt.time().strftime(self.time_format).strip()

        attrs['type'] = _forced_type or 'date'
        attrs['value'] = str_dt
        html_date = u'<input %s>' % get_html_attrs(attrs)

        attrs['type'] = _forced_type or 'time'
        attrs['value'] = str_tt
        html_time = u'<input %s>' % get_html_attrs(attrs)

        return Markup(html_date + html_time)

    def as_input_date(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs.setdefault('required', True)
        attrs['type'] = attrs.get('type') or 'date'

        str_dt = ''
        ldt = self.to_string(**attrs)
        if ldt:
            if isinstance(ldt, list):
                str_dt = ldt[0]
            else:
                str_dt = '{dt.year}-{dt.month:02d}-{dt.day:02d}'.format(dt=ldt.date())

        attrs['value'] = str_dt
        html_date = u'<input %s>' % get_html_attrs(attrs)

        return Markup(html_date)

    def as_input_time(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs.setdefault('required', True)
        attrs['type'] = attrs.get('type') or 'time'

        str_tt = ''
        ldt = self.to_string(**attrs)
        if ldt:
            if isinstance(ldt, list):
                str_tt = ldt[1]
            else:
                str_tt = ldt.time().strftime(self.time_format).strip()

        attrs['value'] = str_tt
        html_time = u'<input %s>' % get_html_attrs(attrs)

        return Markup(html_time)

    def __call__(self, **kwargs):
        return self.as_inputs(**kwargs)

    def str_to_py(self, **kwargs):
        if self.str_value is None:
            return None
        if not isinstance(self.str_value, list):
            return None

        str_dt = self.str_value[0]
        str_tt = '00:00'
        if len(self.str_value) > 1:
            str_tt = self.str_value[1]

        dt = self._str_to_datetime(str_dt)
        if not dt:
            raise ValidationError
        tt = self._str_to_time(str_tt)
        if not tt:
            tt = datetime.time(0, 0, 0)

        dt = dt.replace(hour=tt.hour, minute=tt.minute, second=tt.second)
        return self._to_utc(dt)
