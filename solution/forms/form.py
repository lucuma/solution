# -*- coding: utf-8 -*-
from .fields import Field, FileField


class Form(object):
    """
    """

    def __init__(self, data=None, defaults=None, files=None):
        data = data or {}
        files = files or {}
        self.defaults = defaults
        self.cleaned_data = {}
        self.changed_fields = []
        if data or defaults or files:
            self._init_fields(data, files)

    def _init_fields(self, data, files):
        fields = []
        for name in dir(self):
            if name.startswith('_'):
                continue
            field = getattr(self, name)
            if not isinstance(field, Field):
                continue
            fields.append(name)
            field.name = name

            if not isinstance(field, FileField):
                value = data.get(name, None)
            else:
                value = files.get(name, None)
            
            if value is not None:
                field.value = value
            else:
                python_value = self.defaults.get(name, u'')
                field.load_value(python_value)

        self.fields = fields
        self.validators = getattr('_validate', [])

    @property
    def has_changed(self):
        return bool(self.changed_data)

    def is_valid(self):
        self.cleaned_data = {}
        self.changed_fields = []
        data = {}
        errors = False

        # Validate each field
        for name in self.fields:
            field = getattr(self, name)
            value = field.validate()
            if field.error:
                errors = True
                continue

            data[name] = value
            field.has_changed = value != self.defaults.get(name, u'')
            if field.has_changed:
                self.changed_fields.append(name)
        
        if not errors:
            self.data = data

        # Validate relation between fields
        for v in self.validators:
            if not v(data):
                errors = True
                self.error = ValidationError(v.code, v.message)
                break
        
        return errors

