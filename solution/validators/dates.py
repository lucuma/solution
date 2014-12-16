# coding=utf-8
import datetime

from .validator import Validator


class IsDate(Validator):
    """Validates that the field is a date or a datetime.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date.'

    def __call__(self, py_value=None, form=None):
        return isinstance(py_value, datetime.date)


class IsTime(Validator):
    """Validates that the field is a date or a datetime.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date.'

    def __call__(self, py_value=None, form=None):
        return isinstance(py_value, datetime.time)


class Before(Validator):
    """Validates than the date happens before another.
    This will work with both date and datetime values.

    :param date:
        The latest valid date.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date before %s.'

    def __init__(self, dt, message=None):
        assert isinstance(dt, datetime.date)
        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime(dt.year, dt.month, dt.day)
        self.dt = dt
        if message is None:
            message = self.message % dt.isoformat()
        self.message = message

    def __call__(self, py_value=None, form=None):
        value = py_value
        if not isinstance(value, datetime.date):
            return False
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month, value.day)
        return value <= self.dt


class After(Validator):
    """Validates than the date happens after another.
    This will work with both date and datetime values.

    :param date:
        The soonest valid date.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date after %s.'

    def __init__(self, dt, message=None):
        assert isinstance(dt, datetime.date)
        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime(dt.year, dt.month, dt.day)
        self.dt = dt
        if message is None:
            message = self.message % dt.isoformat()
        self.message = message

    def __call__(self, py_value=None, form=None):
        value = py_value
        if not isinstance(value, datetime.date):
            return False
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime(value.year, value.month, value.day)
        return value >= self.dt


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
        self.dt = datetime.datetime.utcnow()
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
        self.dt = datetime.datetime.utcnow()
        return super(AfterNow, self).__call__(py_value, form)
