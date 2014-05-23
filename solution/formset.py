# -*- coding: utf-8 -*-
from .utils import FakeMultiDict, get_obj_value, set_obj_value


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
    _prefix = u''
    missing_objs = None
    has_changed = False

    def __init__(self, form_class, data=None, objs=None, files=None,
            locale='en', tz='utc', prefix=u'', create_new=True,
            backref=None, parent=None):
        self._form_class = form_class
        self._locale = locale
        self._tz = tz
        self._prefix = prefix
        self._create_new = bool(create_new)
        backref = backref or parent
        self._backref = backref

        self._forms = []
        self._errors = {}
        self.missing_objs = []
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
        missing_objs = []
        num = 0

        for i, obj in enumerate(objs, 1):
            num = i
            form_prefix = self._get_prefix(num)
            if (
                    (data or files)
                    and self._form_class._model
                    and not has_data(data, form_prefix)
                    and not has_data(files, form_prefix)
                ):
                missing_objs.append(obj)
                continue

            f = self._form_class(
                data, obj=obj, files=files,
                locale=self._locale, tz=self._tz,
                prefix=form_prefix, backref=self._backref
            )
            forms.append(f)
        num += 1

        if data and self._create_new:
            forms = self._find_new_forms(forms, num, data, files,
                locale=self._locale, tz=self._tz)

        self._forms = forms
        self.missing_objs = missing_objs
        if self._backref:
            for mo in missing_objs:
                if get_obj_value(mo, self._backref, None):
                    set_obj_value(mo, self._backref, None)

    def _get_prefix(self, num):
        return '{0}{1}.{2}'.format(
            self._prefix,
            self._form_class.__name__.lower(),
            num
        )

    def _find_new_forms(self, forms, num, data, files, locale, tz):
        """Acknowledge new forms created client-side.
        """
        form_prefix = self._get_prefix(num)
        while has_data(data, form_prefix) or has_data(files, form_prefix):
            f = self._form_class(
                data, files=files, locale=locale, tz=tz,
                prefix=form_prefix, backref=self._backref
            )
            forms.append(f)
            num += 1
            form_prefix = self._get_prefix(num)
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
        return [form.save(backref_obj) for form in self._forms]


def has_data(d, prefix):
    """Test if any of the `keys` of the `d` dictionary starts with `prefix`.
    """
    prefix = r'%s-' % (prefix, )
    for k in d:
        if not k.startswith(prefix):
            continue
        return True
    return False

