# -*- coding: utf-8 -*-


class FormValidator(object):
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
    message = u'The {0} doesn\'t match.'
    
    def __init__(self, name1, name2, plural=u'fields', message=None):
        self.name1 = name1
        self.name2 = name2
        if message is None:
            message = self.message.format(plural)
        self.message = message

    def __call__(self, data=None, form=None):
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
        for field in self.fields:
            if data.get(field):
                return True
        return False

