# -*- coding: utf-8 -*-
import re
from xml.sax.saxutils import quoteattr

from . import validators as v
from .utils import to_unicode

try:
    from jinja2 import Markup
except ImportError:
    Markup = to_unicode


class ValidationError(object):

    def __init__(self, code, message):
        self.code = code
        self.message = message


class Field(object):
    """A base form field. All fields must inherit from this class.

    :param validators:
        An iterable of validators. This will evaluate the current `value` when
        the method `validate` is called.

    For extensibility, any named parameter will be stored in `self.extra`.
    """

    _value = u''
    name = 'unnamed'
    hide_value = False
    has_changed = False

    def __init__(self, *validators, **kwargs):
        self.validators = validators
        # Extensibility FTW
        self.extra = kwargs

    def _validator_in(self, validator, validators):
        for v in validators:
            if isinstance(v, validator):
                return True
        return False

    def load_value(self, python_value):
        self._value = self.to_html(python_value)

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value if self._value and not self.hide_value else u''

    value = property(set_value, get_value)

    def to_html(self, python_value):
        return to_unicode(python_value or u'')

    def to_python(self):
        return to_unicode(self.value)

    def validate(self):
        """Validates the current value of a field.
        """
        python_value = self.to_python()
        for v in validators:
            if not v(python_value):
                self.error = ValidationError(v.code, v.message)
                break
        return python_value

    def _get_html_attrs(self, **kwargs):
        """Generate HTML attributes from the provided keyword arguments.

        The output value is sorted by the passed keys, to provide consistent
        output.  Because of the frequent use of the normally reserved keyword
        `class`, `classes` is used instead. Also, all underscores are translated
        to regular dashes.

        >>> _get_html_attrs(id='text1', classes='myclass', data_id=1, checked=True)
        u'class="myclass" data-id="1" id="text1" checked'
        """
        attrs = []
        props = []

        classes = kwargs.get('classes', '').strip()
        if classes:
            classes = ' '.join(re.split(r'\s+', classes))
            classes = to_unicode(quoteattr(classes))
            attrs.append('class=%s' % classes)
        try:
            del kwargs['classes']
        except KeyError:
            pass

        for key, value in kwargs.iteritems():
            key = key.replace('_', '-')
            key = to_unicode(key)
            if value is True:
                props.append(key)
            else:
                value = quoteattr(to_unicode(value))
                attrs.append(u'%s=%s' % (key, value))

        attrs.sort()
        props.sort()
        attrs.extend(props)
        return u' '.join(attrs)

    def __repr__(self):
        raise NotImplemented


class FileField(Field):
    """ An uploaded file field.
    """
    _type = 'file'
    hide_value = True

    def __init__(self, upload=None, *validators, **kwargs):
        self.upload = upload
        super(TextField, self).__init__(*validators, **kwargs)

    def to_python(self, value):
        if self.upload:
            return self.upload(value)
        return super(TextField, self).to_python(value)

    def __repr__(self, **attrs):
        attrs_ = {
            'type': self._type,
        }
        attrs_.update(attrs)
        attrs_['name'] = self.name
        html_attrs = self._get_html_attrs(attrs_)
        html = u'<input %s>' % html_attrs
        return Markup(html)


class TextField(Field):
    """A text field.
    """
    _type = 'text'
    _default_validator = None

    def __init__(self, *validators, **kwargs):
        defval = self._default_validator
        if defval and not self._validator_in(defval, validators):
            validators.append(defval())

        super(TextField, self).__init__(*validators, **kwargs)

    def __repr__(self, **attrs):
        attrs_ = {
            'type': self._type,
        }
        attrs_.update(attrs)
        attrs_['name'] = self.name
        attrs_['value'] = self.value
        html_attrs = self._get_html_attrs(attrs_)
        html = u'<input %s>' % html_attrs
        return Markup(html)

    def as_textarea(self, **attrs):
        value = self.value if not self.hide_value else u''
        attrs['name'] = self.name
        html_attrs = self._get_html_attrs(attrs)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, self.value)
        return Markup(html)


class PasswordField(TextField):
    """A password field.

    For security purposes, this field will not reproduce the value on a form
    submit by default. To have the value filled in, set `hide_value` to
    `False`.
    """
    _type = 'password'

    def __init__(self, hide_value=True):
        self.hide_value = hide_value


class NumberField(TextField):
    """A number field.
    """
    _type = 'number'
    _default_validator = v.IsNumber


class EmailField(TextField):
    """An email field.
    """
    _type = 'email'
    _default_validator = v.IsEmail


class URLField(TextField):
    """An URL field.
    """
    _type = 'url'
    _default_validator = v.IsURL

    def to_python(self):
        #TODO: automatically add the 'http://' part if it doesn't have one
        return to_unicode(self.value)


class DateField(TextField):
    """A date field.
    """
    _type = 'datetime'
    _default_validator = v.IsDate


class DateTimeField(TextField):
    """A datetime field.
    """
    _type = 'datetime'
    _default_validator = v.IsDate


class ColorField(TextField):
    """A color field.
    """
    _type = 'color'


