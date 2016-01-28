# coding=utf-8
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
    _named_errors = None
    missing_objs = None
    has_changed = False

    def __init__(
            self, form_class, data=None, objs=None, files=None,
            locale='en', tz='utc', create_new=True, name='',
            backref=None, parent=None):
        self._form_class = form_class
        self._locale = locale
        self._tz = tz
        self._name = name
        self._create_new = bool(create_new)
        backref = backref or parent
        self._backref = backref

        self._forms = []
        self._errors = {}
        self._named_errors = {}
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
        return self.get_empty_form(1)

    def get_form(self, index):
        """Returns the n-index form, where index is 1-based.
        the form'll be filled with data if it exists or empty if not
        """
        index = max(1, index)
        if len(self._forms) >= index:
            return self._forms[index - 1]
        return self.get_empty_form(index)

    def get_empty_form(self, index):
        """Returns an empty n-index form, where index is 1-based.
        """
        return self._form_class(prefix=self._get_fullname(index))

    def _init(self, data=None, objs=None, files=None):
        self._errors = {}
        self._named_errors = {}
        self.has_changed = False

        data = data or {}
        if not hasattr(data, 'getlist'):
            data = FakeMultiDict(data)
        files = files or {}
        if not hasattr(files, 'getlist'):
            files = FakeMultiDict(files)
        objs = objs or []
        try:
            iter(objs)
        except TypeError:
            objs = [objs]

        forms = []
        missing_objs = []
        num = 0

        for i, obj in enumerate(objs, 1):
            num = i
            fullname = self._get_fullname(num)
            if has_been_deleted(data, fullname):
                missing_objs.append(obj)
                continue

            f = self._form_class(
                data, obj=obj, files=files,
                locale=self._locale, tz=self._tz,
                prefix=fullname, backref=self._backref
            )
            forms.append(f)
        num += 1

        if data and self._create_new:
            forms = self._find_new_forms(
                forms, num, data, files,
                locale=self._locale, tz=self._tz
            )

        self._forms = forms
        self.missing_objs = missing_objs

        # Deattach the missing objects from their former parent
        if self._backref:
            for mo in missing_objs:
                if get_obj_value(mo, self._backref, None):
                    set_obj_value(mo, self._backref, None)

        # Delete the missing objects if possible
        if missing_objs:
            for mo in missing_objs:
                if hasattr(mo, 'db'):
                    mo.db.session.delete(mo)

    def as_dict(self):
        return [form.as_dict() for form in self._forms]

    def _get_fullname(self, num):
        return '{name}.{num}'.format(
            name=self._name or self._form_class.__name__.lower(),
            num=num
        )

    def _find_new_forms(self, forms, num, data, files, locale, tz):
        """Acknowledge new forms created client-side.
        """
        fullname = self._get_fullname(num)
        while has_data(data, fullname) or has_data(files, fullname):
            f = self._form_class(
                data, files=files, locale=locale, tz=tz,
                prefix=fullname, backref=self._backref
            )
            forms.append(f)
            num += 1
            fullname = self._get_fullname(num)
        return forms

    def is_valid(self):
        self._errors = {}
        self._named_errors = {}
        self.has_changed = False
        errors = {}
        named_errors = {}

        for name, form in enumerate(self._forms, 1):
            if not form.has_input_data:
                self.has_changed = True
                continue
            else:
                if not form.is_valid():
                    errors[name] = form._errors
                    named_errors.update(form._named_errors)
                    continue
                if form.has_changed:
                    self.has_changed = True
        if errors:
            self._errors = errors
            self._named_errors = named_errors
            return False
        return True

    def save(self, backref_obj):
        return [
            form.save(backref_obj) for form in self._forms
            if form.has_input_data
        ]


def has_data(d, fullname):
    """Test if any of the `keys` of the `d` dictionary starts with `fullname`.
    """
    fullname = r'%s-' % (fullname, )
    for k in d:
        if not k.startswith(fullname):
            continue
        return True
    return False


def has_been_deleted(d, fullname):
    return '{}__deleted'.format(fullname) in d
