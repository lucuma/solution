# coding=utf-8
from ..utils import Markup, get_html_attrs
from .field import Field


class Text(Field):
    """A text field.

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

    """

    _type = 'text'
    default_validator = None

    def __init__(self, **kwargs):
        kwargs.setdefault('default', u'')
        super(Text, self).__init__(**kwargs)

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        kwargs.setdefault('type', self._type)
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('value', self.to_string(**kwargs))
        if not self.optional:
            kwargs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(kwargs)
        return Markup(html)

    def as_textarea(self, **kwargs):
        kwargs['name'] = self.name
        if not self.optional:
            kwargs.setdefault('required', True)
        html_attrs = get_html_attrs(kwargs)
        value = kwargs.get('value', self.to_string(**kwargs))
        html = u'<textarea %s>%s</textarea>' % (html_attrs, value)
        return Markup(html)
