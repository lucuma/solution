# coding=utf-8
from copy import copy
import inspect

from ._compat import itervalues
from .fields import Field
from .formset import FormSet
from .utils import FakeMultiDict, get_obj_value, set_obj_value


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
        Default locale for this form. Can be overwrited in each field.

    :param tz:
        Default timezone for this field. Can be overwrited in each field.

    :param prefix:
        If provided, all fields will have their name prefixed with the
        value. Used to repeat the form in the same page.

    :param backref:
        .

    """
    _model = None
    _fields = None
    _forms = None
    _sets = None
    _errors = None
    _named_errors = None

    _input_data = None

    cleaned_data = None
    changed_fields = None

    def __init__(self, data=None, obj=None, files=None, locale='en', tz='utc',
                 prefix=u'', backref=None, parent=None):

        backref = backref or parent
        if self._model is not None:
            assert inspect.isclass(self._model)

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
        self._backref = backref

        self.cleaned_data = {}
        self.changed_fields = []
        self.validated = False
        self._obj = obj
        self._errors = {}
        self._named_errors = {}

        self._init_fields()
        # Even when there is no data we need this initialisation
        self._init_data(data, obj, files)

    def _init_fields(self):
        """Creates the `_fields`, `_forms` asn `_sets` dicts.

        Any properties which begin with an underscore or are not `Field`,
        `Form` or `FormSet` **instances** are ignored by this method.
        """
        fields = {}
        forms = {}
        sets = {}

        for name in dir(self):
            if name.startswith('_'):
                continue
            field = getattr(self, name)
            is_field = isinstance(field, Field)
            is_form = isinstance(field, Form) or (
                inspect.isclass(field) and issubclass(field, Form))
            is_set = isinstance(field, FormSet)

            if is_field:
                field = copy(field)
                field.name = self._prefix + name
                field.form = self
                if field.prepare is None:
                    field.prepare = getattr(self, 'prepare_' + name, None)
                if field.clean is None:
                    field.clean = getattr(self, 'clean_' + name, None)
                fields[name] = field
                setattr(self, name, field)
            elif is_form:
                forms[name] = field
            elif is_set:
                field._name = self._prefix + name  # REALLY IMPORTANT
                sets[name] = field

        self._fields = fields
        self._forms = forms
        self._sets = sets

    def prepare(self, data):
        """You can overwrite this method to store the logic of pre-processing
        the input data.
        """
        return data

    def clean(self, cleaned_data):
        """You can overwrite this method to store the logic of post-processing
        the cleaned data after validation.
        You can delete fields but any field that isn't part of the form is
        filtered out.
        """
        return cleaned_data

    def _init_data(self, data, obj, files):
        """Load the data into the form.
        """
        data = self.prepare(data)

        # Initialize sub-forms
        for name, subform in self._forms.items():
            obj_value = get_obj_value(obj, name)
            if inspect.isclass(subform):
                fclass = subform
            else:
                fclass = subform.__class__
            subform_prefix = '{prefix}{name}.'.format(
                prefix=self._prefix,
                name=name.lower()
            )
            subform = fclass(
                data,
                obj_value,
                files=files,
                locale=self._locale,
                tz=self._tz,
                prefix=subform_prefix,
                backref=getattr(subform, '_backref', None)
            )

            self._forms[name] = subform
            setattr(self, name, subform)
            self._input_data = self._input_data or subform._input_data

        # Initialize form-sets
        for name, formset in self._sets.items():
            obj_value = get_obj_value(obj, name)
            sclass = formset.__class__
            formset_name = '{prefix}{name}'.format(
                prefix=self._prefix,
                name=name.lower()
            )
            formset = sclass(
                form_class=formset._form_class,
                name=formset_name,
                data=data,
                objs=obj_value,
                files=files,
                locale=self._locale,
                tz=self._tz,
                create_new=formset._create_new,
                backref=formset._backref
            )
            self._sets[name] = formset
            setattr(self, name, formset)
            for _form in formset._forms:
                self._input_data = self._input_data or _form._input_data

        # Initialize fields
        for name, field in self._fields.items():
            subdata = data.getlist(self._prefix + name)
            subfiles = files.getlist(self._prefix + name)
            self._input_data = self._input_data or subdata or subfiles
            obj_value = get_obj_value(obj, name)
            was_deleted = self._prefix + name + '__deleted' in data
            if was_deleted:
                subdata = obj_value = subfiles = None
            field.load_data(subdata, obj_value, file_data=subfiles,
                            locale=self._locale, tz=self._tz)
            # delete field data
            if was_deleted:
                field._deleted = True

    def reset(self):
        for subform in self._forms.values():
            subform.reset()
        for formset in self._sets.values():
            formset.reset()
        for field in self._fields.values():
            field.reset()

    def __iter__(self):
        """Iterate form fields in arbitrary order.
        """
        return itervalues(self._fields)

    def __getitem__(self, name):
        return self._fields[name]

    def __contains__(self, name):
        return (name in self._fields)

    @property
    def has_input_data(self):
        return bool(self._input_data)

    @property
    def has_changed(self):
        return len(self.changed_fields) > 0

    def is_valid(self):
        """Return whether the current values of the form fields are all valid.
        """
        self.cleaned_data = {}
        self.changed_fields = []
        self.validated = False
        self._errors = {}
        self._named_errors = {}
        cleaned_data = {}
        changed_fields = []
        errors = {}
        named_errors = {}

        # Validate sub forms
        for name, subform in self._forms.items():
            if not subform.is_valid():
                errors[name] = subform._errors
                named_errors.update(subform._named_errors)
                continue
            if subform.has_changed:
                changed_fields.append(name)

        # Validate sub sets
        for name, formset in self._sets.items():
            if not formset.is_valid():
                errors[name] = formset._errors
                named_errors.update(formset._named_errors)
                continue
            if formset.has_changed:
                changed_fields.append(name)

        # Validate each field
        for name, field in self._fields.items():
            field.error = None
            py_value = field.validate(self)
            if field.error:
                errors[name] = field.error
                named_errors[field.name] = field.error
                continue
            cleaned_data[name] = py_value
            if hasattr(field, '_deleted'):
                cleaned_data[name] = None
                field.has_changed = True
            if field.has_changed:
                changed_fields.append(name)

        # Validate relation between fields
        for name, field in self._fields.items():
            field.validate(self, cleaned_data)
            if field.error:
                errors[name] = field.error
                named_errors[field.name] = field.error
                continue

        if errors:
            self._errors = errors
            self._named_errors = named_errors
            return False

        self.changed_fields = changed_fields
        self.cleaned_data = self.clean(cleaned_data)
        self.validated = True
        return True

    def save(self, backref_obj=None):
        """Save the cleaned data to the initial object or creating a new one
        (if a `model_class` was provided).
        """
        if not self.validated:
            assert self.is_valid()

        if self._model and not self._obj:
            obj = self._save_new_object(backref_obj)
        else:
            obj = self.save_to(self._obj)

        for key, subform in self._forms.items():
            data = subform.save(obj)
            if self._model and not data:
                continue
            set_obj_value(obj, key, data)

        for key, formset in self._sets.items():
            data = formset.save(obj)
            if self._model and not data:
                continue
            set_obj_value(obj, key, data)

        return obj

    def _save_new_object(self, backref_obj=None):
        db = self._model.db
        data = dict([
            (key, val) for key, val in self.cleaned_data.items()
            if (
                (not isinstance(getattr(self, key), FormSet)) and
                (not isinstance(getattr(self, key), Form))
            )
        ])
        if self._backref and backref_obj:
            data[self._backref] = backref_obj

        obj = self._model(**data)
        db.add(obj)
        return obj

    def save_to(self, obj):
        """Save the cleaned data to an object.
        """
        if isinstance(obj, dict):
            obj = dict(obj)

        for key in self.changed_fields:
            if key in self.cleaned_data:
                val = self.cleaned_data.get(key)
                set_obj_value(obj, key, val)
        return obj

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
