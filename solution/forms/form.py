# -*- coding: utf-8 -*-
import inspect

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
    :param files:
        Used to pass files coming from the enduser, usually `request.files`,
        or equivalent.
    :param obj:
        If `data` is empty or not provided, this object is checked for
        attributes matching field names.
    :param prefix:
        If provided, all fields will have their name prefixed with the
        value.
    """

    _model = None

    _fields = None
    _forms = None
    _sets = None
    _errors = None
    _first = None

    cleaned_data = None
    changed_fields = None

    def __init__(self, data=None, obj=None, files=None, prefix=u''):
        data = data or {}
        if not hasattr(data, 'getlist'):
            data = FakeMultiDict(data)

        files = files or {}
        if not hasattr(files, 'getlist'):
            files = FakeMultiDict(files)

        obj = obj or {}
        if isinstance(obj, dict):
            obj = FakeMultiDict(obj)

        assert (self._model is None) or issubclass(self._model, Model)
        prefix = prefix or u''
        if prefix and not prefix.endswith(('_', '-', '.', '+', '|')):
            prefix += u'-'
        self._prefix = prefix

        self.cleaned_data = {}
        self.changed_fields = []
        self._obj = obj
        self._errors = {}

        self._init_fields()
        self._init_data(data, obj, files)
    
    def _init_fields(self):
        """Creates the `_fields` and `_forms` dicts, which are dicts of `Field`
        instances and sub `Form` subclasses keyed by name.

        Any properties which begin with an underscore or are not `Field`
        instances or `Form` subclasses are ignored by this method.
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

            if not first and (is_field or is_form or is_set):
                first = name

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
        self._first = first

    def _init_data(self, data, obj, files):
        """Load the data into the form.
        """
        ## Initialize sub-forms
        for name, subform in self._forms.items():
            subobj = getattr(obj, name, None)
            fclass = subform.__class__
            subform = fclass(data, subobj, files=files, prefix=self._prefix)
            self._forms[name] = subform
            setattr(self, name, subform)

        ## Initialize sub-sets
        for name, subset in self._sets.items():
            subobj = getattr(obj, name, None)
            subset._init(data, subobj, files=files)

        ## Initialize fields
        for name, field in self._fields.items():
            value = data.getlist(self._prefix + name)
            if not value:
                value = files.getlist(self._prefix + name)
            if value:
                # `value` is iterable
                field.value = value
            elif obj:
                field.load_value(getattr(obj, name, None))

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
            python_value = field.validate()
            if field.error:
                errors[name] = field.error
                continue

            cleaned_data[name] = python_value
            field.has_changed = (python_value != getattr(self._obj, name, None))
            if field.has_changed:
                changed_fields.append(name)

        ## Validate relation between fields
        for name, field in self._fields.items():
            field.validate(cleaned_data)
            if field.error:
                errors[name] = field.error
                continue

        if errors:
            self._errors = errors
            return False

        self.cleaned_data = cleaned_data
        self.changed_fields = changed_fields
        return True

    def save(self):
        """Save the cleaned data to the initial object or creating a new one
        (if a `model_class` was provided)."""
        if not self.cleaned_data:
            assert self.is_valid

        for subform in self._forms.values():
            subform.save()

        for subset in self._sets.values():
            subset.save()

        if self._model and not self._obj:
            return self._save_new_object()
        return self.save_to(self._obj)

    def _save_new_object(self):
        db = self._model.db
        colnames = self._model.__table__.columns.keys()
        data = {}
        for colname in colnames:
            if colname in self.cleaned_data:
                data[colname] = self.cleaned_data[colname]
        obj = self._model(**data)
        db.add(obj)
        return obj

    def save_to(self, obj):
        """Save the cleaned data to an object."""
        if not self.cleaned_data:
            return
        if isinstance(obj, Model):
            colnames = obj.__table__.columns.keys()
            for colname in colnames:
                if colname in self.cleaned_data:
                    setattr(obj, colname, self.cleaned_data[colname])
        elif isinstance(obj, dict):
            obj.update(self.cleaned_data)
        else:
            for key, value in self.cleaned_data:
                setattr(obj, key, value)
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

    def __init__(self, form_class, data=None, objs=None, files=None):
        self._form_class = form_class
        self._forms = []
        self._errors = {}
        self.has_changed = False
        if (data or objs or files):
            self._init(data, objs, files)

    def __iter__(self):
        """Iterate the bound forms of this set.
        """
        return iter(self._forms)

    @property
    def form(self):
        return self._form_class()

    def _init(self, data=None, objs=None, files=None):
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

        _prefix = 0
        for prefix, obj in enumerate(objs, 1):
            f = self._form_class(data, obj=obj, files=files, prefix=str(prefix))
            forms.append(f)
            _prefix = prefix

        _prefix += 1
        forms = self._find_new_forms(forms, _prefix, data, files)
        self._forms = forms

    def _find_new_forms(self, forms, prefix, data, files):
        """Acknowledge new forms created client-side.
        """
        first_field_name = self._form_class()._first
        pname = '%i-%s' % (prefix, first_field_name)
        while data.get(pname) or files.get(pname):
            f = self._form_class(data, files=files, prefix=str(prefix))
            forms.append(f)
            prefix += 1
            pname = '%i-%s' % (prefix, first_field_name)
        return forms

    def is_valid(self):
        self._errors = {}
        self.has_changed = False
        errors = {}

        for form in self._forms:
            if not form.is_valid():
                errors[name] = form._errors
                continue
            if form.has_changed:
                self.has_changed = True
        if errors:
            self._errors = errors
            return False
        return True

    def save(self):
        for form in self._forms:
            form.save()

