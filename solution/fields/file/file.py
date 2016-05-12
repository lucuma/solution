# coding=utf-8
from werkzeug.datastructures import FileStorage
from solution.fields import Field
from solution.utils import Markup, get_html_attrs

from .helpers import FileSystemUploader


class File(Field):
    """ An upload file field.

    **Does not actually upload the file. Use its ``clean`` method for that.**

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

    """
    _type = 'file'
    hide_value = True

    def __init__(self, base_path='.', **kwargs):
        # Backwards compatibility
        kwargs.setdefault('clean', kwargs.get('upload'))

        self.base_path = base_path
        if base_path is None:
            self.storage = None
        else:
            self.storage = FileSystemUploader(
                base_path=base_path,
                upload_to=kwargs.pop('upload_to', ''),
                secret=kwargs.pop('secret', False),
                prefix=kwargs.pop('prefix', ''),
                allowed=kwargs.pop('allowed', None),
                denied=kwargs.pop('denied', None),
                max_size=kwargs.pop('max_size', None),
            )
        super(File, self).__init__(**kwargs)

    def clean(self, value):
        """Takes a Werkzeug FileStorage, returns the relative path.
        """
        if isinstance(value, FileStorage):
            return self.storage.save(value)
        return value

    def str_to_py(self, **kwargs):
        return self.str_value or self.file_data or self.obj_value

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        attrs = self.extra.copy()
        attrs.update(kwargs)
        attrs.setdefault('type', self._type)
        attrs['name'] = self.name
        if attrs['type'] != self._type:
            attrs['value'] = self.to_string(**attrs)
        if not self.optional and not self.obj_value:
            attrs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(attrs)
        return Markup(html)
