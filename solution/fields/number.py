# -*- coding: utf-8 -*-
from .. import validators as v
from .text import Text


class Number(Text):
    """A number field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

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
    _type = 'number'
    default_validator = v.IsNumber

    def __init__(self, type=float, **kwargs):
        self.type = type
        super(Number, self).__init__(**kwargs)

    def str_to_py(self, *args):
        try:
            num = float(self.str_value)
            if self.type != float:
                num = self.type(num)
            return num 
        except Exception:
            return None

