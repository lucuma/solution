# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime, date
import inspect
import re
from xml.sax.saxutils import quoteattr

from babel.dates import (format_datetime, format_time,
    parse_date, parse_datetime, parse_time)
try:
    from jinja2 import Markup
except ImportError:
    Markup = unicode
from pytz import timezone, utc

from . import validators as v
from ..serializers import to_unicode


__all__ = (
    'Markup', 'ValidationError',

    '_Field', '_Text', '_Password', '_Number', '_NaturalNumber', '_Email',
    '_URL', '_Date', '_Color', '_File', '_Boolean',
    '_Select', '_Collection',

    'Field', 'Text', 'Password', 'Number', 'NaturalNumber', 'Integer', 'Email',
    'URL', 'Date', 'Color', 'File', 'Boolean',
    'Select', 'Collection',
)


class ValidationError(object):

    def __init__(self, code, message):
        self.code = code
        self.message = to_unicode(message) or u''

    def __repr__(self):
        return self.message



#- Real fields
#------------------------------------------------------------------------------#


class _Field(object):
    """The real form field class.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """
    name = 'field'
    locale = 'en'
    tz = utc

    value = None
    obj_value = None

    _default_validator = None
    
    error = None
    has_changed = False

    # Do not show the current value of the field in the HTML
    hide_value = False

    # Indicates that the user hasn't sent data for this field
    empty = True

    def __init__(self, validate=None, default=None, **kwargs):
        validate = validate or []
        defval = self._default_validator
        validate = list(validate)
        if defval and not self._validator_in(defval, validate):
            validate.append(defval())
        self.validators = [val() if inspect.isclass(val) else val
            for val in validate]

        self.optional = not self._validator_in(v.Required, validate)
        self.default = default

        # Extensibility FTW
        self.custom_prepare = kwargs.pop('prepare', None)
        self.custom_clean = kwargs.pop('clean', None)
        self.locale = kwargs.pop('locale', self.locale)
        self.tz = kwargs.pop('tz', self.tz)
        self.extra = kwargs

    def reset(self):
        self.value = None
        self.obj_value = None
        self.empty = True

    def _validator_in(self, validator, validators):
        for v in validators:
            if (v == validator) or isinstance(v, validator):
                return True
        return False

    def load_value(self, data=None, files=None, obj_value=None, locale=None, tz=None):
        self.reset()
        self.empty = not bool(data or files)
        self.value = data or files
        self.obj_value = obj_value
        self.locale = locale or self.locale
        self.tz = tz or self.tz

    def get_value(self):
        value = self.value or self.obj_value
        if isinstance(value, list) and value:
            value = value[0]
        return value

    def prepare(self, value, locale=None, tz=None):
        return to_unicode(value or u'')

    def to_html(self, locale=None, tz=None):
        if self.hide_value:
            return u''
        value = self.get_value()
        if self.custom_prepare:
            value = self.custom_prepare(value, locale, tz)
        value = self.prepare(value, locale, tz)
        return value.strip()

    def clean(self, value, locale=None, tz=None):
        return value

    def to_python(self, locale=None, tz=None):
        value = self.get_value()
        if self.custom_clean:
            value = self.custom_clean(value, locale, tz)
        value = self.clean(value, locale, tz)
        return value

    def validate(self, form=None, cleaned_data=None, locale=None, tz=None):
        """Validates the current value of a field.
        """
        if cleaned_data is None:
            self.error = None
            python_value = self.to_python(locale, tz)

            if isinstance(python_value, ValidationError):
                self.error = python_value
                return None

            self.has_changed = (python_value != self.obj_value)
            # Do not validate optional fields
            if (python_value is None) and self.optional:
                return self.default or None

            return self._validate_value(form, python_value)
        self._validate_form(form, cleaned_data)

    def _validate_value(self, form, python_value):
        for val in self.validators:
            if isinstance(val, v.FormValidator):
                continue
            if not val(python_value, form):
                self.error = ValidationError(val.code, val.message)
                return self.default
        return python_value

    def _validate_form(self, form, cleaned_data):
        for val in self.validators:
            if not isinstance(val, v.FormValidator):
                continue
            if not val(cleaned_data, form):
                self.error = ValidationError(val.code, val.message)
                break

    def _get_html_attrs(self, kwargs=None):
        """Generate HTML attributes from the provided keyword arguments.

        The output value is sorted by the passed keys, to provide consistent
        output.  Because of the frequent use of the normally reserved keyword
        `class`, `classes` is used instead. Also, all underscores are translated
        to regular dashes.

        Set any property with a `True` value.

        >>> _get_html_attrs({'id': 'text1', 'classes': 'myclass',
            'data_id': 1, 'checked': True})
        u'class="myclass" data-id="1" id="text1" checked'

        """
        kwargs = kwargs or {}
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
            if isinstance(value, bool):
                if value is True:
                    props.append(key)
            else:
                value = quoteattr(to_unicode(value))
                attrs.append(u'%s=%s' % (key, value))

        attrs.sort()
        props.sort()
        attrs.extend(props)
        return u' '.join(attrs)

    def __unicode__(self):
        """Returns a HTML representation of the field. For more powerful 
        rendering, see the `__call__` method.
        """
        return self()

    def __str__(self):
        """Returns a HTML representation of the field. For more powerful 
        rendering, see the `__call__` method.
        """
        return self()

    def __html__(self):
        """Returns a HTML representation of the field. For more powerful 
        rendering, see the `__call__` method.
        """
        return self()

    def __call__(self, **kwargs):
        raise NotImplemented


class _Text(_Field):
    """A text field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """
    _type = 'text'
    _default_validator = None

    def __init__(self, **kwargs):
        super(_Text, self).__init__(**kwargs)

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, locale=None, tz=None, **kwargs):
        kwargs['type'] = kwargs.get('type', self._type)
        kwargs['name'] = self.name
        kwargs['value'] = self.to_html(locale, tz)
        if not self.optional:
            kwargs['required'] = True
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<input %s>' % html_attrs
        return Markup(html)

    def as_textarea(self, locale=None, tz=None, **kwargs):
        kwargs['name'] = self.name
        if not self.optional:
            kwargs['required'] = True
        html_attrs = self._get_html_attrs(kwargs)
        value = self.to_html(locale, tz)
        html = u'<textarea %s>%s</textarea>' % (html_attrs, value)
        return Markup(html)


class _Password(_Text):
    """A password field.

    :param hide_value:
        If `True` this field will not reproduce the value on a form
        submit by default. This is the default for security purposes.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone
    
    """
    _type = 'password'
    hide_value = True

    def __init__(self, hide_value=True, **kwargs):
        self.hide_value = hide_value
        super(_Password, self).__init__(**kwargs)


class _Number(_Text):
    """A number field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone
    
    """
    _type = 'number'
    _default_validator = v.IsNumber

    def clean(self, value, locale=None, tz=None):
        try:
            return float(value)
        except Exception:
            return None


class _NaturalNumber(_Text):
    """A natural number (positive integer including zero) field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone
    
    """
    _type = 'number'
    _default_validator = v.IsNaturalNumber

    def clean(self, value, locale=None, tz=None):
        try:
            return int(str(value), 10)
        except Exception:
            return None


class _Email(_Text):
    """An email field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """
    _type = 'email'
    _default_validator = v.ValidEmail


class _URL(_Text):
    """An URL field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """
    _type = 'url'
    _default_validator = v.ValidURL


class _Date(_Text):
    """A date field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """
    _type = 'datetime'
    _default_validator = v.IsDate
    format = 'short'

    def __init__(self, format=None, **kwargs):
        self.format = format
        return super(_Date, self).__init__(**kwargs)

    def prepare(self, value, locale=None, tz=None):
        if isinstance(value, list) and value:
            value = value[0] or u''
        if isinstance(value, date) and not isinstance(value, datetime):
            now = datetime.utcnow()
            value = datetime(value.year, value.month, value.day,
                now.hour, now.minute, now.second)
        return value

    def to_html(self, locale=None, tz=None):
        locale = locale or self.locale or 'en'
        tz = tz or self.tz
        if isinstance(tz, basestring):
            tz = timezone(tz)
        value = self.value
        if isinstance(value, date) and not isinstance(value, datetime):
            now = datetime.utcnow()
            value = datetime(value.year, value.month, value.day,
                now.hour, now.minute, now.second)
        try:
            return format_datetime(value, format=self.format, tzinfo=tz, locale=locale)
        except Exception:
            # raise
            return u''

    def clean(self, value, locale=None, tz=None):
        if not value:
            return None
        locale = locale or self.locale or 'en'
        tz = tz or self.tz
        if isinstance(tz, basestring):
            tz = timezone(tz)
        try:
            try:
                dt = parse_datetime(value, locale=locale)
            except NotImplementedError:
                dt = parse_date(value, locale=locale)
            if isinstance(dt, date) and not isinstance(dt, datetime):
                now = datetime.utcnow()
                dt = datetime(dt.year, dt.month, dt.day,
                    now.hour, now.minute, now.second)
            if tz:
                dt = dt - tz.utcoffset(dt, is_dst=True)
            return dt
        except Exception:
            # raise
            return None


class _Color(_Text):
    """A color field.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone
    
    """
    _type = 'color'
    _default_validator = v.IsColor

    _re_colors = re.compile(
        r'#?(?P<hex>[0-9a-f]){3,8}|'
        r'rgba?\((?P<r>[0-9]+),(?P<g>[0-9]+),(?P<b>[0-9]+)'
        r'(?:,(?P<a>[0-9]+))?\)',
        re.IGNORECASE)

    def clean(self, value, locale=None, tz=None):
        if not value:
            return None
        m = self._re_colors.match(value.replace(' ', ''))
        if not m:
            return None
        md = m.groupdict()
        if 'hex' in md:
            return self._normalize_hex(md['hex'])
        return self._normalize_rgb(md['r'], md['g'], md['b'], md.get('a'))

    def _normalize_hex(self, hc):
        """Transform a xxx hex color to xxxxxx.
        """
        lhc = len(hc)
        if lhc not in (3, 4, 6, 8):
            return None
        hc = hc.lower()
        if lhc >= 6:
            return '#' + hc
        nhc = u'#%s%s%s' % (hc[0] * 2, hc[1] * 2, hc[2] * 2)
        if lhc == 4:
            nhc += hc[3] * 2
        return nhc

    def _normalize_rgb(self, r, g, b, a):
        """Transform a rgb[a] color to #rgb[a].
        """
        r = int(r, 10)
        g = int(g, 10)
        b = int(b, 10)
        if a:
            a = int(a, 10)
        if r > 255 or g > 255 or b > 255 or (a and a > 255):
            return None
        color = '#%02x%02x%02x' % (r, g, b)
        if a:
            color += '%02x' % a
        return color


class _File(_Field):
    """ An uploaded file field.

    :param upload:
        Optional function to be call for doing the actual file upload. It must
        return a python value ready for validation.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone
    
    """
    hide_value = True

    def __init__(self, upload=None, **kwargs):
        self.upload = upload
        super(_File, self).__init__(**kwargs)

    def to_python(self, locale=None, tz=None):
        value = self.value
        if isinstance(value, list) and value:
            value = value[0]
        if not value:
            return self.obj_value
        if not self.upload:
            return value
        try:
            return self.upload(value)
        except Exception, e:
            return ValidationError('invalid_file', str(e))

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        kwargs['type'] = 'file'
        kwargs['name'] = self.name
        if not self.optional:
            kwargs['required'] = True
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<input %s>' % html_attrs
        return Markup(html)


FALSY_VALUES = [u'', u'0', u'no', u'off', u'false',]

class _Boolean(_Field):
    """A True/False field.

    :param falsy:
        A list of raw values considered `False`.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """

    def __init__(self, falsy=FALSY_VALUES, **kwargs):
        self.falsy = falsy
        super(_Boolean, self).__init__(**kwargs)

    def to_python(self, locale=None, tz=None):
        value = self.value
        if not value or (value in self.falsy):
            return False
        return True

    def __call__(self, **kwargs):
        return self.as_checkbox(**kwargs)

    def as_checkbox(self, **kwargs):
        kwargs['type'] = 'checkbox'
        kwargs['name'] = self.name
        if self.value:
            kwargs['checked'] = True
        if not self.optional:
            kwargs['required'] = True
        html_attrs = self._get_html_attrs(kwargs)
        html = u'<input %s>' % html_attrs
        return Markup(html)



#- Multivalue
#------------------------------------------------------------------------------#


class MultiValue(_Field):
    """
    :param filters:
        List of validators. If a value do not pass one of these it'll be
        filtered out from the final result.
    """
    def __init__(self, filters=None, **kwargs):
        filters = filters or []
        self.filters = [f() if inspect.isclass(f) else f for f in filters]
        super(MultiValue, self).__init__(**kwargs)

    def get_value(self):
        values = self.value or self.obj_value
        if not values:
            return []
        if isinstance(values, list):
            return values
        return [values]

    def prepare(self, values, locale=None, tz=None):
        if self.custom_prepare:
            values_ = []
            for val in values:
                try:
                    val = self.custom_prepare(val, locale, tz)        
                except (TypeError, ValueError):
                    try:
                        val = self.custom_prepare(val)        
                    except (TypeError, ValueError):
                        continue
                if val:
                    values_.append(val)
            values = values_
        return values

    def clean(self, values, locale=None, tz=None):
        for f in self.filters:
            values = filter(f, values)

        if self.custom_clean:
            values_ = []
            for val in values:
                try:
                    val = self.custom_clean(val, locale, tz)        
                except (TypeError, ValueError):
                    try:
                        val = self.custom_clean(val)        
                    except (TypeError, ValueError):
                        continue
                if val:
                    values_.append(val)
            values = values_
        return filter(lambda v: bool(v), values)

    def to_python(self, locale=None, tz=None):
        values = self.get_value()
        values = self.clean(values, locale, tz)
        return values


class _Select(MultiValue):
    """A field with a fixed list of options for the values

    :param items:
        Either: 
        - An list of tuples with the format `(value, label)`; or
        - A function that return a list of items in that format.

    :param multiple:
        Whether or not more than one value can be selected

    :param filters:
        List of validators. If a value do not pass one of these it'll be
        filtered out from the final result.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """

    def __init__(self, items, multiple=False, **kwargs):
        self.items = items
        self.multiple = multiple
        super(_Select, self).__init__(**kwargs)

    def get_items(self):
        return self.items() if callable(self.items) else self.items

    def __iter__(self):
        items = self.get_items()
        for item in items:
            yield item

    def to_html(self, locale=None, tz=None):
        if self.hide_value:
            return []
        values = self.get_value()
        return self.prepare(values, locale, tz)

    def to_python(self, locale=None, tz=None):
        values = self.get_value()
        values = self.clean(values, locale, tz)
        if self.multiple:
            return values
        return values[0]

    def __call__(self, **kwargs):
        items = self.get_items()
        if len(items) > 5:
            return self.as_select(_items=items, **kwargs)
        if self.multiple:
            return self.as_checkboxes(_items=items, **kwargs)
        return self.as_radiobuttons(_items=items, **kwargs)

    def as_select(self, _items=None, **kwargs):
        """Render the field as `<select multiple>` element.
        
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`
        
        """
        kwargs['name'] = self.name
        kwargs['multiple'] = self.multiple
        if not self.optional:
            kwargs['required'] = True
        html_attrs = self._get_html_attrs(kwargs)
        html = [u'<select %s>' % html_attrs]

        if _items is None:
            _items = self.get_items()
        curr_values = self.to_html()

        for value, label in _items:
            item_attrs = {'value': value}
            if value in curr_values or str(value) in curr_values:
                item_attrs['selected'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(u'<option %s>%s</option>' % (html_attrs, label))
        html.append(u'</select>')
        return Markup('\n'.join(html))

    def as_checkboxes(self, _items=None,
            tmpl=u'<label><input %(attrs)s> %(label)s</label>', **kwargs):
        """Render the field as a series of checkboxes, using the `tmpl`
        parameter as the template.

        :param tmpl:
            HTML template to use for rendering each item.
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`

        """
        if _items is None:
            _items = self.get_items()
        kwargs['type'] = 'checkbox'
        kwargs['name'] = self.name
        html = []
        curr_values = self.to_html()
        
        for value, label in _items:
            item_attrs = kwargs.copy()
            item_attrs['value'] = value
            if value in curr_values or str(value) in curr_values:
                item_attrs['checked'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(tmpl % {'attrs': html_attrs, 'label': label, 'value': value})
        return Markup('\n'.join(html))

    def as_radiobuttons(self, _items=None, 
            tmpl=u'<label><input %(attrs)s> %(label)s</label>', **kwargs):
        """Render the field as a series of radio buttons, using the `tmpl`
        parameter as the template.
        
        :param tmpl:
            HTML template to use for rendering each item.
        :param **kwargs:
            Named paremeters used to generate the HTML attributes of each item.
            It follows the same rules as `Field._get_html_attrs`
        
        """
        if _items is None:
            _items = self.get_items()
        kwargs['type'] = 'radio'
        kwargs['name'] = self.name
        html = []
        
        curr_values = self.to_html()
        if not isinstance(curr_values, list):
            curr_values = [curr_values]

        for value, label in _items:
            item_attrs = kwargs.copy()
            item_attrs['value'] = value
            if value in curr_values or str(value) in curr_values:
                item_attrs['checked'] = True
            html_attrs = self._get_html_attrs(item_attrs)
            html.append(tmpl % {'attrs': html_attrs, 'label': label, 'value': value})
        return Markup('\n'.join(html))


class _Collection(_Text, MultiValue):
    """A field that takes an open number of values of the same kind.
    For example, a list of comma separated tags or email addresses.

    :param sep:
        String to separate each value.
        When joining the values to render, it is used as-is. When splitting
        the user input, however, is tranformed first to a regexp
        when the spaces around the separator are ignored.

    :param filters:
        List of validators. If a value do not pass one of these it'll be
        filtered out from the final result.

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that preprocess the value before loading.

    :param clean:
        An optional function that takes the value and return a 'cleaned'
        version of it. If the value raise an exception, `None` must be
        returned instead.

    :param locale:
        Default locale

    :param tz:
        Default timezone

    """
    _type = 'text'

    def __init__(self, sep=', ', **kwargs):
        self.sep = sep
        self.rxsep = r'\s*%s\s*' % self.sep.replace(' ', '')
        super(_Collection, self).__init__(**kwargs)

    def get_value(self):
        values = self.value or self.obj_value
        if not values:
            return []
        if isinstance(values, list):
            return values
        return re.split(self.rxsep, values)

    def to_html(self, locale=None, tz=None):
        if self.hide_value:
            return u''
        values = self.get_value()
        values = self.prepare(values, locale, tz)
        html = to_unicode(self.sep.join(values)) or u''
        return html.strip()



#- Field factories
#------------------------------------------------------------------------------#


class Field(object):
    """A form field factory. All field factories must inherit from this class.
    """
    _class = _Field

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def make(self):
        return self._class(*self.args, **self.kwargs)


class Text(Field):
    _class = _Text

class Password(Field):
    _class = _Password

class Number(Field):
    _class = _Number

class NaturalNumber(Field):
    _class = _NaturalNumber    

class Integer(Field):
    _class = _NaturalNumber 

class Email(Field):
    _class = _Email

class URL(Field):
    _class = _URL

class Date(Field):
    _class = _Date

class Color(Field):
    _class = _Color

class File(Field):
    _class = _File    

class Boolean(Field):
    _class = _Boolean

class Select(Field):
    _class = _Select

class Collection(Field):
    _class = _Collection

