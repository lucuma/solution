# -*- coding: utf-8 -*-
import datetime

from .validator import Validator


class Before(Validator):
    """Validates than the date happens before another.
    This will work with both date and datetime values.

    :param date:
        The latest valid date. 

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date before %s.'

    def __init__(self, date, message=None):
        assert isinstance(date, datetime.date)
        if not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month. date.day)
        self.date = date
        if message is None:
            message = self.message.format(date.isoformat())
        self.message = message

    def __call__(self, py_value=None, form=None):
        value = py_value
        if not isinstance(value, datetime.date):
            return False
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month. value.day)
        return value <= self.date


class After(Validator):
    """Validates than the date happens after another.
    This will work with both date and datetime values.

    :param date:
        The soonest valid date. 

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date after {0}.'

    def __init__(self, date, message=None):
        assert isinstance(date, datetime.date)
        if not isinstance(date, datetime.datetime):
            date = datetime.datetime(date.year, date.month. date.day)
        self.date = date
        if message is None:
            message = self.message.format(date.isoformat())
        self.message = message

    def __call__(self, py_value=None, form=None):
        value = py_value
        if not isinstance(value, datetime.date):
            return False
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month. value.day)
        return value >= self.date


class BeforeNow(Before):
    """Validates than the date happens before now.
    This will work with both date and datetime values.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date in the past.'

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        self.date = datetime.datetime.utcnow()
        return super(BeforeNow, self).__call__(py_value, form)


class AfterNow(After):
    """Validates than the date happens after now.
    This will work with both date and datetime values.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date in the future.'

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        self.date = datetime.datetime.utcnow()
        return super(AfterNow, self).__call__(py_value, form)

