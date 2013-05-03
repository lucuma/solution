# -*- coding: utf-8 -*-
import datetime

from .validator import Validator


class Required(Validator):
    """Validates that the field contains data.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'This field is required.'

    def __call__(self, py_value=None, form=None):
        return py_value is not None


class IsNumber(Validator):
    """Validates that the field is a number (integer or floating point).

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a number.'

    def __call__(self, py_value=None, form=None):
        try:
            float(py_value)
        except Exception:
            return False
        return True


class IsDate(Validator):
    """Validates that the field is a date or a datetime.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid date.'

    def __call__(self, py_value=None, form=None):
        return isinstance(py_value, datetime.date)

