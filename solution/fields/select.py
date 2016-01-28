# coding=utf-8
from __future__ import absolute_import
from hashlib import md5

from .._compat import to_unicode, string_types
from ..utils import Markup, get_html_attrs, escape
from .field import Field


TMPL = u'<label><input {attrs}> {label}</label>'


def iter_flatten(iterable):
    items = iter(iterable)
    for i in items:
        if isinstance(i, string_types):
            continue
        if isinstance(i, list):
            for f in iter_flatten(i):
                yield f
        else:
            yield str(i[0])


class BaseSelect(Field):

    def _clean_value(self, value):
        if not self._type:
            return value
        try:
            return self._type(value)
        except (ValueError, TypeError):
            return None

    def _render_optgroup(self, items, values):
        html = []
        label = items[0]
        if isinstance(label, string_types):
            label = escape(label)
            html.append(u'<optgroup label="%s">' % (label, ))
            items = items[1:]
        else:
            html.append(u'<optgroup>')

        for item in items:
            html.append(self._render_option(item, values))
        html.append(u'</optgroup>')
        return html

    def _render_option(self, item, values):
        val, label = item
        item_attrs = {'value': val}
        item_attrs['selected'] = (val in values or str(val) in values)
        html_attrs = get_html_attrs(item_attrs)
        return u'<option %s>%s</option>' % (html_attrs, escape(label))

    def _render_fieldset(self, items, kwargs, values, tmpl):
        html = [u'<fieldset>']
        legend = items[0]
        if isinstance(legend, string_types):
            html.append(u'<legend>%s</legend>' % (legend, ))
            items = items[1:]

        for item in items:
            html.append(self._render_item(item, kwargs, values, tmpl))
        html.append(u'</fieldset>')
        return html

    def _render_item(self, item, kwargs, values, tmpl):
        val, label = item
        item_id = u'{id}-{hash}'.format(
            id=self.id,
            hash=md5(label.encode('utf8')).hexdigest()[:8],
        )
        kwargs['value'] = val
        kwargs['checked'] = (val in values or str(val) in values)
        html_attrs = get_html_attrs(kwargs)
        return (
            tmpl
            .replace(u'{attrs}', html_attrs)
            .replace(u'{label}', escape(label))
            .replace(u'{value}', escape(val))
            .replace(u'{id}', escape(item_id))
        )


class Select(BaseSelect):

    """A field with a fixed list of options for the possible values

    :param items:
        Either:
        - An list of tuples with the format `(value, label)`; or
        - A function that return a list of items in that format.

    :param create:
        If False, only the values in the items are allowed as valid.
        Set to True with caution.

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

    def __init__(self, items, type=None, create=False, **kwargs):
        self._items = items
        self._type = type
        self._create = create
        super(Select, self).__init__(**kwargs)

    @property
    def items(self):
        if callable(self._items):
            return self._items(self.form)
        return self._items

    def __iter__(self):
        for item in self.items:
            yield item

    def str_to_py(self, **kwargs):
        if self._create:
            return self._clean_value(self.str_value)

        accepted = iter_flatten(self.items)
        if self.str_value in accepted:
            return self._clean_value(self.str_value)
        return None

    def __call__(self, **kwargs):
        items = self.items
        if len(items) > 5:
            return self.as_select(_items=items, **kwargs)
        return self.as_radios(_items=items, **kwargs)

    def as_dict(self):
        dd = Field.as_dict(self)
        dd['items'] = self.items
        return dd

    def as_select(self, _items=None, **kwargs):
        """Render the field as a `<select>` element.

        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `get_html_attrs`

        """
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs['required'] = True
        html = [u'<select %s>' % get_html_attrs(attrs)]
        values = [self.to_string(**attrs)] or []
        items = _items or self.items

        for item in items:
            if isinstance(item, list):
                html.extend(self._render_optgroup(item, values))
            else:
                html.append(self._render_option(item, values))
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
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['type'] = 'radio'
        attrs['name'] = self.name
        html = []
        tmpl = to_unicode(tmpl)
        values = [self.to_string(**attrs)] or []
        items = _items or self.items

        for item in items:
            if isinstance(item, list):
                html.extend(self._render_fieldset(item, attrs, values, tmpl))
            else:
                html.append(self._render_item(item, attrs, values, tmpl))

        return Markup('\n'.join(html))

    as_radiobuttons = as_radios


class MultiSelect(BaseSelect):

    """Like a ``:class:solution.Select``but allows to choose more than one
    option at a time.

    :param items:
        Either:
        - An list of tuples with the format `(value, label)`; or
        - A function that return a list of items in that format.

    :param create:
        If False, only the values in the items are allowed as valid.
        Set to True with caution.

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

    def __init__(self, items, type=None, create=False, **kwargs):
        kwargs.setdefault('default', [])
        self._items = items
        self._type = type
        self._create = create
        super(MultiSelect, self).__init__(**kwargs)

    @property
    def items(self):
        if callable(self._items):
            return self._items(self.form)
        return self._items

    def __iter__(self):
        for item in self.items:
            yield item

    def as_dict(self):
        dd = Field.as_dict(self)
        dd['items'] = self.items
        dd['value'] = dd.get('value') or []
        return dd

    def _clean_data(self, str_value, file_data, obj_value):
        """This overwrite is neccesary for work with multivalues"""
        str_value = str_value or None
        obj_value = obj_value or None
        return (str_value, None, obj_value)

    def py_to_str(self, **kwargs):
        return self.obj_value or self.default

    def str_to_py(self, **kwargs):
        if self.str_value is None:
            return None

        if self._create:
            py_value = [self._clean_value(v) for v in self.str_value]
        else:
            accepted = list(iter_flatten(self.items))
            py_value = [self._clean_value(v)
                        for v in self.str_value if v in accepted]
        return py_value or None

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
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['name'] = self.name
        if not self.optional:
            attrs['required'] = True
        html = [u'<select %s multiple>' % get_html_attrs(attrs)]
        values = self.to_string(**attrs) or []
        items = _items or self.items

        for item in items:
            if isinstance(item, list):
                html.extend(self._render_optgroup(item, values))
            else:
                html.append(self._render_option(item, values))
        html.append(u'</select>')

        return Markup('\n'.join(html))

    def as_checks(self, tmpl=TMPL, _items=None, **kwargs):
        """Render the field as a series of checkboxes, using the `tmpl`
        parameter as the template for each item.

        :param tmpl:
            HTML template to use for rendering each item.

        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `get_html_attrs`

        """
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs['type'] = 'checkbox'
        attrs['name'] = self.name
        html = []
        tmpl = to_unicode(tmpl)
        values = self.to_string(**attrs) or []
        items = _items or self.items

        for item in items:
            if isinstance(item, list):
                html.extend(self._render_fieldset(item, attrs, values, tmpl))
            else:
                html.append(self._render_item(item, attrs, values, tmpl))
        return Markup('\n'.join(html))

    as_checkboxes = as_checks
