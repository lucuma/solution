# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ..utils import Markup, get_html_attrs
from .field import Field, ValidationError


class File(Field):
    """ An uploaded file field.

    :param upload:
        Optional function to be call for doing the actual file upload. It must
        return a python value ready for cleaning and validation or raise a
        ``solution.ValidationError`` in case of errors.

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

    :param locale:
        Default locale for this field. Overwrite the form locale.

    :param tz:
        Default timezone for this field. Overwrite the form timezone.
    
    """
    hide_value = True

    def __init__(self, upload=None, **kwargs):
        self.upload = upload
        super(File, self).__init__(**kwargs)

    def str_to_py(self, *args):
        value = self.str_value or self.file_data
        if not value:
            return self.obj_value
        if not self.upload:
            return value
        return self.upload(value)

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        kwargs['type'] = 'file'
        kwargs['name'] = self.name
        if not self.optional:
            kwargs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(kwargs)
        return Markup(html)

