# coding=utf-8
# from .._compat import string_types
from .validator import Validator
from .._compat import string_types


class Required(Validator):
    """Validates that the field contains data.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'This field is required.'

    def __call__(self, py_value=None, form=None):
        if isinstance(py_value, string_types):
            return bool(py_value.strip())
        return py_value not in ('', None)


class IsNumber(Validator):
    """Validates that the field is a number (integer or floating point).

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a number.'

    def __call__(self, py_value=None, form=None):
        if py_value is None or py_value == u'':
            return True
        try:
            float(py_value)
        except Exception:
            return False
        return True
