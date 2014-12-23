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
        self.storage = FileSystemUploader(
            base_path=base_path,
            upload_to=kwargs.get('upload_to', ''),
            secret=kwargs.get('secret', False),
            prefix=kwargs.get('prefix', ''),
            allowed=kwargs.get('allowed', None),
            denied=kwargs.get('denied', None),
            max_size=kwargs.get('max_size', None),
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
        kwargs.setdefault('type', self._type)
        kwargs['name'] = self.name
        if kwargs['type'] != self._type:
            kwargs['value'] = self.to_string(**kwargs)
        if not self.optional and not self.obj_value:
            kwargs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(kwargs)
        return Markup(html)
