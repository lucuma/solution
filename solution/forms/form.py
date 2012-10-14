# -*- coding: utf-8 -*-
from __future__ import absolute_import

from pytz import utc

from .. import Model
from .fields import Field, File
from .utils import FakeMultiDict


__all__ = ('Form', 'FormSet')


class Form(object):
    """Declarative Form base class. Provides core behaviour like field
    construction, validation, and data and error proxying.

    :param data:
        Used to pass data coming from the enduser, usually `request.form`,
        `request.POST` or equivalent.
    :param obj:
        If `data` is empty or not provided, this object is checked for
        attributes matching field names.
    :param files:
        Used to pass files coming from the enduser, usually `request.files`,
        or equivalent.
    :param locale:
        .
    :param tz:
        .
    :param prefix:
        If provided, all fields will have their name prefixed with the
        value.
    :param parent:
        .

    """

    _model = None

    _fields = None
    _forms = None
    _sets = None
    _errors = None

    cleaned_data = None
    changed_fields = None

    def __init__(self, data=None, obj=None, files=None, locale='en', tz=utc,
            prefix=u'', parent=None):
        assert (self._model is None) or issubclass(self._model, Model)
        data = data or {}
        if not hasattr(data, 'getlist'):
            data = FakeMultiDict(data)

        files = files or {}
        if not hasattr(files, 'getlist'):
            files = FakeMultiDict(files)

        obj = obj or {}
        if isinstance(obj, dict):
            obj = FakeMultiDict(obj)

        self._locale = locale
        self._tz = tz
        prefix = prefix or u''
        if prefix and not prefix.endswith(('_', '-', '.', '+', '|')):
            prefix += u'-'
        self._prefix = prefix
        self._parent = parent

        self.cleaned_data = {}
        self.changed_fields = []
        self._obj = obj
        self._errors = {}

        self._init_fields()
        self._init_data(data, obj, files)
    
    def _init_fields(self):
        """Creates the `_fields`, `_forms` asn `_sets` dicts.

        Any properties which begin with an underscore or are not `Field`,
        `Form` or `FormSet` **instances** are ignored by this method.
        """
        fields = {}
        forms = {}
        sets = {}
        first = u''

        for name in dir(self):
            if name.startswith('_'):
                continue
            field = getattr(self, name)
            is_field = isinstance(field, Field)
            is_form = isinstance(field, Form)
            is_set = isinstance(field, FormSet)

            if is_field:
                field = field.make()
                field.name = self._prefix + name
                fields[name] = field
                setattr(self, name, field)
            elif is_form:
                forms[name] = field
            elif is_set:
                sets[name] = field

        self._fields = fields
        self._forms = forms
        self._sets = sets

    def _init_data(self, data, obj, files):
        """Load the data into the form.
        """
        ## Initialize sub-forms
        for name, subform in self._forms.items():
            original_value = getattr(obj, name, None)
            fclass = subform.__class__
            subform = fclass(data, original_value, files=files,
                locale=self._locale, tz=self._tz,
                prefix=self._prefix, parent=subform._parent)
            self._forms[name] = subform
            setattr(self, name, subform)

        ## Initialize sub-sets
        for name, subset in self._sets.items():
            original_value = getattr(obj, name, None)
            subset._init(data, original_value, files=files,
                locale=self._locale, tz=self._tz)

        ## Initialize fields
        for name, field in self._fields.items():
            subdata = data.getlist(self._prefix + name)
            subfiles = files.getlist(self._prefix + name)
            original_value = getattr(obj, name, None)
            field._init(subdata, original_value, files=subfiles,
                locale=self._locale, tz=self._tz)

    def reset(self):
        ## Reset sub-forms
        for subform in self._forms.values():
            subform.reset()

        ## Reset sub-sets
        for subset in self._sets.values():
            subset.reset()

        ## Reset fields
        for field in self._fields.values():
            field.reset()

    def __iter__(self):
        """Iterate form fields in arbitrary order.
        """
        return self._fields.itervalues()

    def __contains__(self, name):
        """Returns `True` if the there is a field with that name in the form.
        """
        return (name in self._fields)

    @property
    def has_changed(self):
        return len(self.changed_fields) > 0

    def is_valid(self):
        """Return whether the current values of the form fields are all valid.
        """
        self.cleaned_data = {}
        self.changed_fields = []
        self._errors = {}
        cleaned_data = {}
        changed_fields = []
        errors = {}

        ## Validate sub forms
        for name, subform in self._forms.items():
            if not subform.is_valid():
                errors[name] = subform._errors
                continue
            if subform.has_changed:
                changed_fields.append(name)

        ## Validate sub sets
        for name, subset in self._sets.items():
            if not subset.is_valid():
                errors[name] = subset._errors
                continue
            if subset.has_changed:
                changed_fields.append(name)

        ## Validate each field
        for name, field in self._fields.items():
            field.error = None
            python_value = field.validate(self)
            if field.error:
                errors[name] = field.error
                continue
            cleaned_data[name] = python_value
            if field.has_changed:
                changed_fields.append(name)

        ## Validate relation between fields
        for name, field in self._fields.items():
            field.validate(self, cleaned_data)
            if field.error:
                errors[name] = field.error
                continue

        if errors:
            self._errors = errors
            return False

        self.cleaned_data = cleaned_data
        self.changed_fields = changed_fields
        return True

    def save(self, parent_obj=None):
        """Save the cleaned data to the initial object or creating a new one
        (if a `model_class` was provided)."""
        if not self.cleaned_data:
            assert self.is_valid
        if self._model and not self._obj:
            obj = self._save_new_object(parent_obj)
        else:
            obj = self.save_to(self._obj)

        for subform in self._forms.values():
            subform.save(obj)

        for subset in self._sets.values():
            subset.save(obj)

        return obj

    def _save_new_object(self, parent_obj=None):
        db = self._model.db
        colnames = self._model.__table__.columns.keys()
        data = {}
        for colname in colnames:
            if colname in self.cleaned_data:
                data[colname] = self.cleaned_data[colname]
        
        if self._parent and parent_obj:
            data[self._parent] = parent_obj

        obj = self._model(**data)
        db.add(obj)
        return obj

    def save_to(self, obj):
        """Save the cleaned data to an object."""
        if not self.cleaned_data:
            return
        if isinstance(obj, Model):
            colnames = self._model.__table__.columns.keys()
            for colname in colnames:
                if colname in self.changed_fields:
                    setattr(obj, colname, self.cleaned_data.get(colname))
            return obj

        if isinstance(obj, dict):
            for key in self.changed_fields:
                obj[key] = self.cleaned_data.get(key)
        else:
            for key in self.changed_fields:
                setattr(obj, key, self.cleaned_data.get(key))
        return obj

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class FormSet(object):
    """Open set of forms. This is intended to be used as in two different ways:
    A. As a field in another form
    B. As a independent form generator
    
    :param form_class:
        The base form class.
    :param data:
        Used to pass data coming from the enduser, usually `request.form`,
        `request.POST` or equivalent.
    :param obj:
        If `data` is empty or not provided, this object is checked for
        attributes matching field names.
    :param files:
        Used to pass files coming from the enduser, usually `request.files`,
        or equivalent.

    """

    _forms = None
    _errors = None
    has_changed = False

    def __init__(self, form_class, parent=None,
            create_new=True, data=None, objs=None, files=None):
        self._form_class = form_class
        self._parent = parent
        self._create_new = bool(create_new)
        self._forms = []
        self._errors = {}
        self.has_changed = False
        if (data or objs or files):
            self._init(data, objs, files)

    def reset(self):
        ## Reset sub-forms
        for subform in self._forms:
            subform.reset()

    def __iter__(self):
        """Iterate the bound forms of this set.
        """
        return iter(self._forms)

    @property
    def form(self):
        return self._form_class(prefix=self._get_prefix(1))

    def _init(self, data=None, objs=None, files=None, locale='en', tz=utc):
        self._errors = {}
        self.has_changed = False

        data = data or {}
        if not hasattr(data, 'getlist'):
            data = FakeMultiDict(data)
        files = files or {}
        if not hasattr(files, 'getlist'):
            files = FakeMultiDict(files)
        objs = objs or []
        try:
            _ = iter(objs)
        except TypeError:
            objs = [objs]

        forms = []
        missing_objs = []
        _prefix = 0

        for num, obj in enumerate(objs, 1):
            _prefix = num
            prefix = self._get_prefix(_prefix)
            if (data or files) and self._form_class._model and \
                    not has_data(data, prefix) and not has_data(files, prefix):
                missing_objs.append(obj)
                continue
            f = self._form_class(data, obj=obj, files=files,
                locale=locale, tz=tz, prefix=prefix, parent=self._parent)
            forms.append(f)

        _prefix += 1
        if data and self._create_new:
            forms = self._find_new_forms(forms, _prefix, data, files,
                locale, tz)

        self._forms = forms
        self.missing_objs = missing_objs

    def _get_prefix(self, num):
        return '%s.%s' % (self._form_class.__name__.lower(), num)

    def _find_new_forms(self, forms, _prefix, data, files, locale, tz):
        """Acknowledge new forms created client-side.
        """
        prefix = self._get_prefix(_prefix)
        while has_data(data, prefix) or has_data(files, prefix):
            f = self._form_class(data, files=files, locale=locale, tz=tz,
                prefix=prefix, parent=self._parent)
            forms.append(f)
            _prefix += 1
            prefix = self._get_prefix(_prefix)
        return forms

    def is_valid(self):
        self._errors = {}
        self.has_changed = False
        errors = {}

        for name, form in enumerate(self._forms, 1):
            if not form.is_valid():
                errors[name] = form._errors
                continue
            if form.has_changed:
                self.has_changed = True
        if errors:
            self._errors = errors
        return True

    def save(self, parent_obj):
        for form in self._forms:
            form.save(parent_obj)


def has_data(d, prefix):
    """Test if any of the `keys` of the `d` dictionary starts with `prefix`.
    """
    prefix = r'%s-' % (prefix, )
    for k in d:
        if not k.startswith(prefix):
            continue
        return True
    return False

