# -*- coding: utf-8 -*-
from .fields import Field, File


class FakeMultiDict(dict):
    """Adds a fake `getlist` method to a regular dict; or act as a proxy to
    Webob's MultiDict `getall` method. 
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError, error:
            raise AttributeError(error)

    def getlist(self, name):
        if hasattr(self, 'getall'):
            return self.getall(name)
        value = self.get(name)
        if value is None:
            return []
        return [value]


class Form(object):
    """
    :param data:
        Used to pass data coming from the enduser, usually `request.form`,
        `request.POST` or equivalent.
    :param files:
        Used to pass files coming from the enduser, usually `request.files`,
        or equivalent.
    :param obj:
        If `data` is empty or not provided, this object is checked for
        attributes matching form field names, which will be used for field
        values.
    """    
    cleaned_data = None
    changed_fields = None
    _initial_data = None

    def __new__(cls, *args, **kwargs):
        """Collect the fields into _fields and name them.
        """
        cls._fields = {}
        for name in dir(cls):
            if name.startswith('_'):
                continue
            field = getattr(cls, name)
            if not isinstance(field, Field):
                continue
            field.name = name
            cls._fields[name] = field
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, data=None, obj=None, files=None):
        data = data or {}
        if not hasattr(data, 'getlist'):
            data = FakeMultiDict(data)

        files = files or {}
        if not hasattr(files, 'getlist'):
            files = FakeMultiDict(files)

        obj = obj or {}
        if isinstance(obj, dict):
            obj = FakeMultiDict(obj)

        self.cleaned_data = {}
        self.changed_fields = []
        self._obj = obj
        self._errors = {}   # List of all errors, for testing
        self._init_data(data, files, obj)

    def _init_data(self, data, files, obj):
        """Load the data into the form.
        """
        no_initial_data = not (data or files or obj)

        for name, field in self._fields.iteritems():
            field.reset()
            if no_initial_data:
                continue
            # Load initial data
            if not isinstance(field, File):
                value = data.getlist(name)
            else:
                value = files.getlist(name)
            # `value` is now a list
            if value:
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
        return bool(self.changed_fields)

    def is_valid(self):
        """Return whether the current values of the form fields are all valid.
        """
        self.cleaned_data = {}
        self.changed_fields = []
        self._errors = {}
        cleaned_data = {}
        errors = {}

        # Validate each field
        for name, field in self._fields.items():
            value = field.validate()
            if field.error:
                errors[name] = field.error
                continue

            cleaned_data[name] = value
            field.has_changed = value != getattr(self._obj, name, None)
            if field.has_changed:
                self.changed_fields.append(name)

        # Validate relation between fields
        for name, field in self._fields.items():
            field.validate(cleaned_data)
            if field.error:
                errors[name] = field.error
                continue
        
        if errors:
            self._errors = errors
            return False
        self.cleaned_data = cleaned_data
        return True

    def save(self):
        """Save the cleaned data to the initial object."""
        self.save_to(self._obj)

    def save_to(self, obj):
        """Save the cleaned data to an object."""
        if not self.cleaned_data:
            return
        for key, value in self.cleaned_data.items():
            setattr(obj, key, value)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
        
