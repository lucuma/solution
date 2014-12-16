# coding=utf-8


class Validator(object):
    """Base field Validator.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Invalid value.'

    def __init__(self, message=None):
        if message is not None:
            self.message = message

