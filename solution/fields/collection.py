# coding=utf-8
from __future__ import absolute_import
import inspect
import re

from .field import Field
from .text import Text


class Collection(Text):
    """A field that takes an open number of values of the same kind.
    For example, a list of comma separated tags or email addresses.

    :param sep:
        String to separate each value.
        When joining the values to render, it is used as-is. When splitting
        the user input, however, is tranformed first to a regexp
        when the spaces around the separator are ignored.

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
    _type = 'text'

    def __init__(self, sep=', ', filters=None, **kwargs):
        kwargs.setdefault('default', [])
        self.sep = sep
        self.rxsep = r'\s*%s\s*' % re.escape(self.sep.replace(' ', ''))
        filters = filters or []
        self.filters = [f() if inspect.isclass(f) else f for f in filters]
        super(Collection, self).__init__(**kwargs)

    def as_dict(self):
        dd = Field.as_dict(self)
        dd['value'] = self._split_values(self.str_value) or []
        return dd

    def _clean_data(self, str_value, file_data, obj_value):
        if isinstance(str_value, (list, tuple)):
            if len(str_value):
                str_value = str_value[0]
            else:
                str_value = None
        if str_value:
            str_value = self.sep.join(self._split_values(str_value))

        if not isinstance(obj_value, (list, tuple)):
            if obj_value:
                obj_value = [obj_value]
            else:
                obj_value = None

        return (str_value, None, obj_value)

    def str_to_py(self, **kwargs):
        if self.str_value is None:
            return None
        py_values = self._split_values(self.str_value)
        if not self.filters:
            return py_values

        final_values = []
        for val in py_values:
            for f in self.filters:
                if not f(val):
                    break
            else:
                # only executed if the loop `for f in self.filters` has
                # exited normally, so the value has passed all filters.
                final_values.append(val)
        return final_values

    def py_to_str(self, **kwargs):
        if not self.obj_value:
            return self.default or u''
        return self.sep.join(self.obj_value)

    def _split_values(self, str_value):
        if not str_value:
            return []
        values = re.split(self.rxsep, str_value.strip())
        return filter(lambda x: x != u'', values)
