# -*- coding: utf-8 -*-
from .utils import FakeMultiDict


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

    def __init__(self, form_class, backref=None, parent=None,
            create_new=True, data=None, objs=None, files=None):
        backref = backref or parent
        self._form_class = form_class
        self._backref = backref
        self._create_new = bool(create_new)
        self._forms = []
        self._errors = {}
        self.has_changed = False
        if (data or objs or files):
            self._init(data, objs, files)

    def reset(self):
        # Reset sub-forms
        for subform in self._forms:
            subform.reset()

    def __len__(self):
        return len(self._forms)

    def __iter__(self):
        """Iterate the bound forms of this set.
        """
        return iter(self._forms)

    def __nonzero__(self):
        return len(self._forms) > 0

    @property
    def form(self):
        return self._form_class(prefix=self._get_prefix(1))

    def _init(self, data=None, objs=None, files=None, locale='en', tz='utc'):
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

            f = self._form_class(
                data, obj=obj, files=files, locale=locale, tz=tz,
                prefix=prefix, backref=self._backref
            )
            forms.append(f)

        _prefix += 1
        if data and self._create_new:
            forms = self._find_new_forms(forms, _prefix, data, files,
                                         locale=locale, tz=tz)
        self._forms = forms
        self.missing_objs = missing_objs
        for mo in missing_objs:
            if getattr(mo, self._backref, None):
                setattr(mo, self._backref, None)

    def _get_prefix(self, num):
        return '%s.%s' % (self._form_class.__name__.lower(), num)

    def _find_new_forms(self, forms, _prefix, data, files, locale, tz):
        """Acknowledge new forms created client-side.
        """
        prefix = self._get_prefix(_prefix)
        while has_data(data, prefix) or has_data(files, prefix):
            f = self._form_class(
                data, files=files, locale=locale, tz=tz,
                prefix=prefix, backref=self._backref
            )
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
            return False
        return True

    def save(self, backref_obj):
        for form in self._forms:
            form.save(backref_obj)


def has_data(d, prefix):
    """Test if any of the `keys` of the `d` dictionary starts with `prefix`.
    """
    prefix = r'%s-' % (prefix, )
    for k in d:
        if not k.startswith(prefix):
            continue
        return True
    return False

