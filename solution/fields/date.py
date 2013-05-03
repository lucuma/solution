# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import date, datetime

from .. import validators as v
from .text import Text

from babel.dates import (format_datetime, format_time,
    parse_date, parse_datetime, parse_time)
from pytz import timezone, utc


class Date(Text):
    """A date field.

    :param format:
        When returned as a string, the value will be printed using this format.

    :param dayfirst:
        This option allow one to change the precedence in which days are
        parsed in ambiguous date strings. If dayfirst is False, the
        MM-DD-YYYY format will have precedence over DD-MM-YYYY.
        `True` by default.

    :param yearfirst:
        This option allow one to change the precedence in which years are
        parsed in ambiguous date strings. If yearfirst is false, the MM-DD-YY
        format will have precedence over YY-MM-DD. `True` by default.

    :param fuzzy:
        If fuzzy is set to True, unknown tokens in the string are ignored
        during parsing. `False` by default.

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

    :param locale:
        Default locale for this field. Overwrite the form locale.

    :param tz:
        Default timezone for this field. Overwrite the form timezone.

    """
    _type = 'text' # This can be date, datetime, time, etc.
    default_validator = v.IsDate
    format = 'short'

    def __init__(self, format=None, dayfirst=True, yearfirst=True,
            fuzzy=False, **kwargs):
        self.format = format
        self.dayfirst = dayfirst
        self.yearfirst = yearfirst
        self.fuzzy = fuzzy

        default = kwargs.get('default')
        if default and not isinstance(default, datetime):
            kwargs['default'] = datetime(default.year, default.month, default.day)
        return super(Date, self).__init__(**kwargs)

    def default_prepare(self, value, locale=None, tz=None):
        if isinstance(value, list) and value:
            value = value[0] or u''
        if isinstance(value, date) and not isinstance(value, datetime):
            now = datetime.utcnow()
            value = datetime(value.year, value.month, value.day,
                now.hour, now.minute, now.second)
        return value

    def to_string(self, locale=None, tz=None):
        locale = locale or self.locale or 'en'
        tz = tz or self.tz
        if isinstance(tz, basestring):
            tz = timezone(tz)
        value = self.get_value()
        if isinstance(value, date) and not isinstance(value, datetime):
            now = datetime.utcnow()
            value = datetime(value.year, value.month, value.day,
                now.hour, now.minute, now.second)
        try:
            return format_datetime(value, format=self.format, tzinfo=tz, locale=locale)
        except Exception:
            # raise
            return u''

    def parse_date(self, string, format='yyyy-MM-dd'):
        """Parse a date from a string.
        
        This function is a fork of `babel.dates.parse_date`.
        
        >>> parse_date('4/1/04', format='M/d/yy')
        datetime.date(2004, 4, 1)
        >>> parse_date('01.04.2004', format='dd.MM.yyyy')
        datetime.date(2004, 4, 1)

        :param string:
        :param format: 
        :return: the parsed date
        :rtype: `date`

        """
        format = format.lower()
        year_idx = format.index('y')
        month_idx = format.index('m')
        if month_idx < 0:
            month_idx = format.index('l')
        day_idx = format.index('d')

        indexes = [(year_idx, 'Y'), (month_idx, 'M'), (day_idx, 'D')]
        indexes.sort()
        indexes = dict([(item[1], idx) for idx, item in enumerate(indexes)])

        # FIXME: this currently only supports numbers, but should also support month
        #        names, both in the requested locale, and english

        numbers = re.findall('(\d+)', string)
        year = numbers[indexes['Y']]
        if len(year) == 2:
            year = 2000 + int(year)
        else:
            year = int(year)
        month = int(numbers[indexes['M']])
        day = int(numbers[indexes['D']])
        if month > 12:
            month, day = day, month
        return date(year, month, day)

    def default_clean(self, value, locale=None, tz=None):
        if not value:
            return None
        locale = locale or self.locale or 'en'
        tz = tz or self.tz
        if isinstance(tz, basestring):
            tz = timezone(tz)
        try:
            if isinstance(value, date):
                dt = value
            else:
                dt = self.parse_date(value, self.format)

            if isinstance(dt, date) and not isinstance(dt, datetime):
                now = datetime.utcnow()
                dt = datetime(dt.year, dt.month, dt.day,
                    now.hour, now.minute, now.second)
            if tz:
                if tz == utc:
                    dt = dt - tz.utcoffset(dt)
                else:
                    dt = dt - tz.utcoffset(dt, is_dst=True)
            return dt
        except Exception:
            raise
            return None

