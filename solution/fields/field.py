# coding=utf-8
from hashlib import md5
import inspect
import os

from .. import validators as v
from .._compat import to_unicode, implements_to_string
from ..utils import Markup, get_html_attrs


class ValidationError(Exception):
    def __init__(self, message=u'Validation error'):
        self.message = message  # Py3 compatibility
        super(ValidationError, self).__init__(message)


@implements_to_string
class Field(object):

    """
    Base class for all fields.

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

    :param optional:
        Do not validate if the value is empty. Default True unless the Required
        validator is present

    """
    name = 'field'
    form = None
    default_validator = None

    str_value = None
    obj_value = None
    error = None
    has_changed = False
    empty = True

    def __init__(self, validate=None, default=None, prepare=None, clean=None,
                 hide_value=False, optional=None, **kwargs):
        self._set_validators(validate)
        self._default = default
        self.prepare = prepare
        self.clean = clean or getattr(self, 'clean', None)
        self.hide_value = hide_value
        if optional is None:
            optional = not validator_in(v.Required, self.validators)
        self.optional = optional
        self.extra = kwargs

    def _set_validators(self, validators):
        validators = validators or []
        if not isinstance(validators, list):
            validators = [validators]
        defval = self.default_validator
        if defval and not validator_in(defval, validators):
            validators.append(defval)
        self.validators = [
            val() if inspect.isclass(val) else val for val in validators]

    @property
    def required(self):
        return not self.optional

    @property
    def default(self):
        if callable(self._default):
            return self._default()
        return self._default

    @property
    def id(self):
        if not hasattr(self, '_id'):
            self._id = self._get_id()
        return self._id

    def _get_id(self):
        return u'id-{name}-{random}'.format(
            name=self.name,
            random=md5(os.urandom(8)).hexdigest()[:8]
        )

    def reset(self):
        self.str_value = None
        self.obj_value = None
        self.file_data = None
        self.empty = True

    def load_data(self, str_value=None, obj_value=None,
                  file_data=None, **kwargs):
        str_value, file_data, obj_value = self._clean_data(
            str_value, file_data, obj_value)
        if self.prepare:
            obj_value = self.prepare(obj_value, **kwargs)
        self.str_value = str_value
        self.file_data = file_data
        self.obj_value = obj_value
        self.empty = not bool(str_value or file_data or obj_value)

    def _clean_data(self, str_value, file_data, obj_value):
        if isinstance(str_value, (list, tuple)):
            if len(str_value):
                str_value = str_value[0]
            else:
                str_value = None
        if isinstance(file_data, (list, tuple)):
            if len(file_data):
                file_data = file_data[0]
            else:
                file_data = None
        return (str_value, file_data, obj_value)

    def __nonzero__(self):
        return not self.empty

    def to_string(self, **kwargs):
        if self.hide_value:
            return u''
        return self.get_str_value(**kwargs)

    def get_str_value(self, **kwargs):
        if self.str_value is None:
            return self.py_to_str(**kwargs)
        return self.str_value

    def py_to_str(self, **kwargs):
        return to_unicode(self.obj_value or self.default)

    def to_python(self, **kwargs):
        try:
            return self.str_to_py(**kwargs)
        except ValidationError as error:
            self.error = error
            return None

    def str_to_py(self, **kwargs):
        if self.str_value is None:
            return self.obj_value
        return self.str_value

    def validate(self, form=None, cleaned_data=None, **kwargs):
        if cleaned_data is None:
            return self.validate_field(form, **kwargs)
        self.validate_form(form, cleaned_data)

    def validate_field(self, form, **kwargs):
        self.error = None
        py_value = self.to_python(**kwargs)
        # Do not validate empty fields if are optional
        if self.optional and self.is_empty(py_value):
            py_value = self.default or py_value
        else:
            py_value = self.validate_value(form, py_value)

        py_value = self.clean_value(py_value, **kwargs)
        self.has_changed = (py_value != self.obj_value)
        return py_value

    def clean_value(self, py_value, **kwargs):
        if not self.clean:
            return py_value
        try:
            return self.clean(py_value, **kwargs)
        except ValidationError as error:
            self.error = error
            return None

    def is_empty(self, py_value):
        return not py_value

    def validate_value(self, form, py_value):
        for validator in self.validators:
            if isinstance(validator, v.FormValidator):
                continue
            if not validator(py_value, form):
                self.error = ValidationError(validator.message)
                return None
        return py_value

    def validate_form(self, form, cleaned_data):
        for validator in self.validators:
            if not isinstance(validator, v.FormValidator):
                continue
            if not validator(cleaned_data, form):
                self.error = ValidationError(validator.message)
                break

    def __str__(self):
        """Returns a HTML representation of the field. For more powerful
        rendering, see the `__call__` method.
        """
        return to_unicode(self())

    def __html__(self):
        """Returns a HTML representation of the field. For more powerful
        rendering, see the `__call__` method.
        """
        return to_unicode(self())

    def __call__(self, **kwargs):
        raise NotImplementedError

    @property
    def value(self):
        return self.to_string()

    def label_tag(self, text, tmpl=u'<label {attrs}>{msg}</label>', **kwargs):
        html = tmpl.format(
            attrs=get_html_attrs(kwargs),
            msg=text,
        )
        return Markup(html)

    def error_tag(self, tmpl=u'<div {attrs}>{msg}</div>', **kwargs):
        if self.error is None:
            return u''
        kwargs.setdefault('classes', u'error')
        html = tmpl.format(
            attrs=get_html_attrs(kwargs),
            msg=self.error.message,
        )
        return Markup(html)


def validator_in(validator, validators_list):
    for val in validators_list:
        if (val == validator) or isinstance(val, validator):
            return True
    return False
