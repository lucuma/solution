# coding=utf-8
from .._compat import to_unicode, string_types
from .validator import Validator


class LongerThan(Validator):
    """Validates the length of a value is longer or equal than minimum.

    :param length:
        The minimum required length of the value.

    :param message:
        Error message to raise in case of a validation error

    """
    message = u'Field must be at least %s character long.'

    def __init__(self, length, message=None):
        assert isinstance(length, int)
        self.length = length
        if message is None:
            message = self.message % (length,)
        self.message = message

    def __call__(self, py_value=None, form=None):
        if py_value is None:
            return False
        py_value = to_unicode(py_value)
        return len(py_value) >= self.length


class ShorterThan(Validator):
    """Validates the length of a value is shorter or equal than maximum.

    :param length:
        The maximum allowed length of the value.

    :param message:
        Error message to raise in case of a validation error

    """
    message = u'Field cannot be longer than %s character.'

    def __init__(self, length, message=None):
        assert isinstance(length, int)
        self.length = length
        if message is None:
            message = self.message % (length,)
        self.message = message

    def __call__(self, py_value=None, form=None):
        if py_value is None:
            return False
        py_value = to_unicode(py_value or u'')
        return len(py_value) <= self.length


class LessThan(Validator):
    """Validates that a value is less or equal than another.
    This will work with integers, floats, decimals and strings.

    :param value:
        The maximum value acceptable.

    :param message:
        Error message to raise in case of a validation error
    """
    message = u'Number must be less than %s.'

    def __init__(self, value, message=None):
        self.value = value
        if message is None:
            message = self.message % (value,)
        self.message = message

    def __call__(self, py_value=None, form=None):
        if isinstance(py_value, string_types):
            py_value = try_to_number(py_value)
        if py_value is None:
            return False
        value = py_value or 0
        return value <= self.value


class MoreThan(Validator):
    """Validates that a value is greater or equal than another.
    This will work with any integers, floats, decimals and strings.

    :param value:
        The minimum value acceptable.

    :param message:
        Error message to raise in case of a validation error
    """
    message = u'Number must be greater than %s.'

    def __init__(self, value, message=None):
        self.value = value
        if message is None:
            message = self.message % (value,)
        self.message = message

    def __call__(self, py_value=None, form=None):
        if isinstance(py_value, string_types):
            py_value = try_to_number(py_value)
        if py_value is None:
            return False
        value = py_value or 0
        return value >= self.value


class InRange(Validator):
    """Validates that a value is of a minimum and/or maximum value.
    This will work with integers, floats, decimals and strings.

    :param minval:
        The minimum value acceptable.

    :param maxval:
        The maximum value acceptable.

    :param message:
        Error message to raise in case of a validation error
    """
    message = u'Number must be between %s and %s.'

    def __init__(self, minval, maxval, message=None):
        self.minval = minval
        self.maxval = maxval
        if message is None:
            message = self.message % (minval, maxval)
        self.message = message

    def __call__(self, py_value=None, form=None):
        if isinstance(py_value, string_types):
            py_value = try_to_number(py_value)
        if py_value is None:
            return False
        value = py_value or 0
        if value < self.minval:
            return False
        if value > self.maxval:
            return False
        return True


def try_to_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return value
