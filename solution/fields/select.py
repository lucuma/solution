# -*- coding: utf-8 -*-
from .._compat import to_unicode
from ..utils import Markup, get_html_attrs
from .field import Field


TMPL = u'<label><input {attrs}> {label}</label>'


class Select(Field):

    """A field with a fixed list of options for the possible values

    :param items:
        Either:
        - An list of tuples with the format `(value, label)`; or
        - A function that return a list of items in that format.

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

    def __init__(self, items, type=None, **kwargs):
        self._items = items
        self.type = type
        super(Select, self).__init__(**kwargs)

    @property
    def items(self):
        if callable(self._items):
            return self._items()
        return self._items

    def __iter__(self):
        for item in self.items:
            yield item

    def str_to_py(self, **kwargs):
        accepted = [str(item[0]) for item in self]
        if self.str_value in accepted:
            return self._clean_value(self.str_value)
        return None

    def _clean_value(self, value):
        if not self.type:
            return value
        try:
            return self.type(value)
        except (ValueError, TypeError):
            return None

    def __call__(self, **kwargs):
        items = self.items
        if len(items) > 5:
            return self.as_select(_items=items, **kwargs)
        return self.as_radios(_items=items, **kwargs)

    def as_select(self, _items=None, **kwargs):
        """Render the field as a `<select>` element.

        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `get_html_attrs`

        """
        kwargs['name'] = self.name
        if not self.optional:
            kwargs['required'] = True
        html = [u'<select %s>' % get_html_attrs(kwargs)]
        value = self.to_string(**kwargs)
        items = _items or self.items

        for val, label in items:
            item_attrs = {'value': val}
            item_attrs['selected'] = (str(val) == str(value))
            html_attrs = get_html_attrs(item_attrs)
            html.append(u'<option %s>%s</option>' % (html_attrs, label))
        html.append(u'</select>')

        return Markup('\n'.join(html))

    def as_radios(self, tmpl=TMPL, _items=None, **kwargs):
        """Render the field as a series of radio buttons, using the `tmpl`
        parameter as the template for each item.

        :param tmpl:
            HTML template to use for rendering each item.

        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `get_html_attrs`

        """
        kwargs['type'] = 'radio'
        kwargs['name'] = self.name
        html = []
        value = self.to_string(**kwargs)
        items = _items or self.items

        for val, label in items:
            kwargs['value'] = val
            kwargs['checked'] = (str(val) == str(value))
            html_attrs = get_html_attrs(kwargs)
            item_html = (tmpl
                         .replace(u'{attrs}', html_attrs)
                         .replace(u'{label}', label)
                         .replace(u'{value}', to_unicode(val))
                         )
            html.append(item_html)

        return Markup('\n'.join(html))


class MultiSelect(Field):

    """Like a ``:class:solution.Select``but allows to choose more than one
    option at a time.

    :param items:
        Either:
        - An list of tuples with the format `(value, label)`; or
        - A function that return a list of items in that format.

    :param filters:
        List of callables (can be validators). If a value do not pass one
        of these (the callable return `False`), it is filtered out from the
        final result.

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

    def __init__(self, items, type=None, **kwargs):
        kwargs.setdefault('default', [])
        self._items = items
        self.type = type
        super(MultiSelect, self).__init__(**kwargs)

    @property
    def items(self):
        if callable(self._items):
            return self._items()
        return self._items

    def __iter__(self):
        for item in self.items:
            yield item

    def _clean_data(self, str_value, file_data, obj_value):
        str_value = str_value or None
        obj_value = obj_value or None
        return (str_value, None, obj_value)

    def py_to_str(self, **kwargs):
        return self.obj_value

    def str_to_py(self, **kwargs):
        if self.str_value is None:
            return None
        accepted = [str(item[0]) for item in self]
        py_value = [self._clean_value(v)
                    for v in self.str_value if v in accepted]
        return py_value or None

    def _clean_value(self, value):
        if not self.type:
            return value
        try:
            return self.type(value)
        except (ValueError, TypeError):
            return None

    def __call__(self, **kwargs):
        items = self.items
        if len(items) > 5:
            return self.as_select(_items=items, **kwargs)
        return self.as_checkboxes(_items=items, **kwargs)

    def as_select(self, _items=None, **kwargs):
        """Render the field as a `<select>` element.

        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `get_html_attrs`

        """
        kwargs['name'] = self.name
        if not self.optional:
            kwargs['required'] = True
        html = [u'<select %s>' % get_html_attrs(kwargs)]
        values = self.to_string(**kwargs) or []
        items = _items or self.items

        for val, label in items:
            item_attrs = {'value': val}
            item_attrs['selected'] = (val in values or str(val) in values)
            html_attrs = get_html_attrs(item_attrs)
            html.append(u'<option %s>%s</option>' % (html_attrs, label))
        html.append(u'</select>')

        return Markup('\n'.join(html))

    def as_checkboxes(self, tmpl=TMPL, _items=None, **kwargs):
        """Render the field as a series of checkboxes, using the `tmpl`
        parameter as the template for each item.

        :param tmpl:
            HTML template to use for rendering each item.

        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `get_html_attrs`

        """
        kwargs['type'] = 'checkbox'
        kwargs['name'] = self.name
        html = []
        values = self.to_string(**kwargs) or []
        items = _items or self.items

        for val, label in items:
            kwargs['value'] = val
            kwargs['checked'] = (val in values or str(val) in values)
            html_attrs = get_html_attrs(kwargs)
            item_html = (tmpl
                         .replace(u'{attrs}', html_attrs)
                         .replace(u'{label}', label)
                         .replace(u'{value}', to_unicode(val))
                         )
            html.append(item_html)

        return Markup('\n'.join(html))

    as_checks = as_checkboxes

