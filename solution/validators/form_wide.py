# coding=utf-8
import datetime

from .validator import Validator


class FormValidator(Validator):
    """Base Form Validator."""
    pass


class AreEqual(FormValidator):
    """Form validator that assert that two fields have the same value.

    :param name1:
        Name of the first field

    :param name2:
        Name of the second field

    :param plural:
        Collective name of the fields. Eg.: 'passwords'

    :param message:
        Custom error message.

    """
    message = u'The %s doesn\'t match.'

    def __init__(self, name1, name2, message=None, plural=u'fields'):
        self.name1 = name1
        self.name2 = name2
        if message is None:
            message = self.message % (plural,)
        self.message = message

    def __call__(self, data=None, form=None):
        data = data or {}
        return data.get(self.name1) == data.get(self.name2)


class AtLeastOne(FormValidator):
    """Form validator that assert that at least of these fields have
    have been filled.

    :param fields:
        Name of the fields.

    :param message:
        Custom error message.

    """
    message = u'Fill at least one of these fields.'

    def __init__(self, fields, message=None):
        self.fields = fields
        if message is not None:
            self.message = message

    def __call__(self, data=None, form=None):
        data = data or {}
        for field in self.fields:
            if data.get(field):
                return True
        return False


class ValidSplitDate(FormValidator):
    """Form validator that assert that a date splitted in two or three separate
    fields is valid.

    :param day:
        Name of the day field.

    :param month:
        Name of the month field.

    :param year:
        Name of the year field (optional, assumed the current one).

    :param message:
        Custom error message.

    """
    message = u'This is not a valid date.'

    def __init__(self, day, month, year=None, message=None):
        self.day = day
        self.month = month
        self.year = year
        if message is not None:
            self.message = message

    def __call__(self, data=None, form=None):
        data = data or {}
        now = datetime.date.today()
        try:
            day = int(data.get(self.day))
            month = int(data.get(self.month))
            year = int(data.get(self.year)) if self.year else None
            if year:
                d = datetime.date(year, month, day)
            else:
                d = datetime.date(now.year, month, day)
        except Exception:
            return False
        return True

