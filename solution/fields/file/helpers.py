# coding=utf-8
from __future__ import print_function

import errno
from math import ceil
import os
import shutil
import uuid

try:
    from werkzeug.exceptions import RequestEntityTooLarge, UnsupportedMediaType
    from werkzeug.utils import secure_filename
except ImportError as e:
    print(e)


IMAGES = ('.jpg', '.jpeg', '.png', '.gif', '.bmp',)

DOCUMENTS = ('.pdf', '.rtf', '.txt', '.md', '.mdown', '.rst',
             '.odf', '.odp', '.ods', '.odg', '.ott', '.otp', '.ots', '.otg',
             '.pages', '.key', '.numbers', '.gnumeric', '.abw',
             '.doc', '.ppt', '.xls', '.vsd',
             '.docx', '.pptx', '.xlsx', '.vsx',
             )

DATA = ('.csv', '.json', '.xml', '.ini', '.plist', '.yaml', '.yml',)

ARCHIVES = ('.zip', '.gz', '.bz2', '.tar', '.7z',)


def get_random_filename():
    return str(uuid.uuid4())


def get_unique_filename(root_path, path, name, ext=''):
    """ """
    path = os.path.join(root_path, path)
    abspath = os.path.abspath(path)
    i = 0
    while True:
        if i:
            filename = u'{0}_{1}'.format(name, i)
            filename = secure_filename(filename)
        else:
            filename = secure_filename(name)
        if ext:
            filename = u'{0}.{1}'.format(filename, ext.strip('.'))
        filepath = os.path.join(abspath, filename)
        if not os.path.exists(filepath):
            break
        i += 1
    return filename


def make_dirs(root_path, filepath):
    fullpath = os.path.join(root_path, filepath)
    fullpath = os.path.abspath(fullpath)
    try:
        os.makedirs(fullpath)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return fullpath


def remove_dir(path):
    try:
        shutil.rmtree(path)
    except OSError:
        pass


def get_box(imw, imh, width, height, x=0, y=0):
    if isinstance(x, basestring):
        if x.endswith('%'):
            x = imw * int(x[:-1]) / 100
        elif x == 'center':
            x = (imw - width) / 2
        elif x.endswith('px'):
            x = x[:-2]

    x = int(x)

    if isinstance(y, basestring):
        if y.endswith('%'):
            y = int(imh * int(y[:-1]) / 100)
        elif y == 'center':
            y = (imh - height) / 2
        elif y.endswith('px'):
            y = int(y[:-2])

    y = int(y)

    # Do not overflow
    if width + x > imw:
        width = imw - x
    if height + y > imh:
        height = imh - y

    return x, y, x + width, y + height


def set_geometry(im, width_height):
    """Rescale the image to the new geometry.
    """
    width, height = width_height
    if not width and not height:
        return im

    im_width, im_height = im.size

    # Geometry match the current size?
    if (width is None) or (im_width == width):
        if (height is None) or (im_height == height):
            return im

    ratio = float(im_width) / im_height

    if width and height:
        new_width = width
        new_height = int(ceil(width / ratio))
        if new_height < height:
            new_height = height
            new_width = int(ceil(height * ratio))
    elif height:
        new_width = int(ceil(height * ratio))
        new_height = height
    else:
        new_width = width
        new_height = int(ceil(width / ratio))

    im.resize(new_width, new_height)
    box = get_box(new_width, new_height, width, height)
    im.crop(*box, reset_coords=True)

    return im


def resize_image(path, width_height):
    from wand.image import Image

    width, height = width_height
    im = Image(filename=path)
    im = set_geometry(im, width_height)

    _, format = os.path.splitext(path)
    format = format[1:]
    im.format = format.lower()
    im.save(filename=path)
    im.close()


class Uploader(object):

    def get_content_length(self, filesto):
        content_length = filesto.content_length
        if content_length == 0:
            filesto.seek(0, 2)
            content_length = filesto.tell()
            filesto.seek(0, 0)
        return content_length

    def validate(self, filesto, allowed, denied, max_size=None):
        max_size = max_size or self.max_size
        content_length = self.get_content_length(filesto)

        if max_size and content_length > max_size:
            raise RequestEntityTooLarge

        original_filename = filesto.filename
        name, ext = os.path.splitext(original_filename)
        ext = ext.lower()
        self.check_file_extension(ext, allowed, denied)

    def check_file_extension(self, ext, allowed, denied):
        if allowed is not True and not ext in allowed:
            raise UnsupportedMediaType()
        if denied and ext in denied:
            raise UnsupportedMediaType()


class FileSystemUploader(Uploader):

    def __init__(self, base_path, upload_to='', secret=False,
                 prefix='', allowed=None, denied=None, max_size=None):
        """
        Except for `base_path`, all of these parameters are optional,
        so only bother setting the ones relevant to your application.

        base_path
        :   Absolute path where the files will be stored. Example:
            `/var/www/example.com/media`.

            MEDIA_DIR = realpath(join(BASE_DIR, 'media'))

        base_url
        :   The base path used when building the file's URL. By default
            is `/static/media`.

            UPLOADS_URL = '/media'

        upload_to
        :   Relative path.
            Instead of a string, this can also be a callable.

        secret
        :   If True, instead of the original filename, a random one'll
             be used.

        prefix
        :   To avoid race-co[nditions between users uploading files with
            the same name at the same time. If `secret` is True, this
            will be ignored.

        allowed
        :   List of allowed fi]le extensions. `True` to allow all
            of them. If the uploaded file doesn't have one of these
            extensions, an `UnsupportedMediaType` exception will be
            raised.

        denied
        :   List of forbidden extensions. Set to `None` to disable.
            If the uploaded file *does* have one of these extensions, a
            `UnsupportedMediaType` exception will be raised.

        max_size
        :   Maximum file size, in bytes, that file can have.
            Note: The `request` attribute `max_content_length`, if defined,
            has higher priority.

        """

        self.base_path = base_path.rstrip('/')
        try:
            os.makedirs(os.path.realpath(base_path))
        except (OSError) as e:
            if e.errno != errno.EEXIST:
                raise

        self.upload_to = upload_to
        self.secret = secret
        self.prefix = prefix
        self.allowed = allowed or IMAGES
        self.denied = denied or []
        self.max_size = max_size

    def save(self, filesto, upload_to=None, name=None, secret=None, prefix=None,
             allowed=None, denied=None, max_size=None, **kwargs):
        """
        Except for `filesto`, all of these parameters are optional, so only
        bother setting the ones relevant to *this upload*.

        filesto
        :   A `werkzeug.FileUploader`.

        upload_to
        :   Relative path to where to upload

        secret
        :   If True, instead of the original filename, a random one'll
             be used.

        prefix
        :   To avoid race-conditions between users uploading files with
            the same name at the same time. If `secret` is True, this
            will be ignored.

        name
        :   If set, it'll be used as the name of the uploaded file.
            Instead of a string, this can also be a callable.

        allowed
        :   List of allowed file extensions. `None` to allow all
            of them. If the uploaded file doesn't have one of these
            extensions, an `UnsupportedMediaType` exception will be
            raised.

        denied
        :   List of forbidden extensions. Set to `None` to disable.
            If the uploaded file *does* have one of these extensions, a
            `UnsupportedMediaType` exception will be raised.

        max_size
        :   Maximum file size, in bytes, that file can have.
            Note: The attribute `max_content_length` defined in the
            `request` object has higher priority.

        """
        if not filesto:
            return None
        upload_to = upload_to or self.upload_to
        secret = secret or self.secret
        prefix = prefix or self.prefix
        original_filename = filesto.filename
        allowed = allowed or self.allowed
        denied = denied or self.denied

        self.validate(filesto, allowed, denied, max_size)

        if callable(upload_to):
            filepath = upload_to(original_filename)
        else:
            filepath = upload_to

        oname, ext = os.path.splitext(original_filename)
        if name:
            new_name = name(original_filename) if callable(name) else name
        else:
            new_name = get_random_filename() if secret else prefix + oname

        filename = get_unique_filename(self.base_path, filepath, new_name, ext=ext)
        fullpath = os.path.join(
            make_dirs(self.base_path, filepath),
            filename
        )
        filesto.save(fullpath)
        filesize = os.path.getsize(fullpath)

        # Post validation
        if max_size and filesize > max_size:
            self.delete_file(fullpath)
            raise RequestEntityTooLarge

        return os.path.join(filepath, filename)

    __call__ = save

    def delete_file(self, filename):
        try:
            os.remove(os.path.join(self.base_path, filename).encode('utf8'))
        except:
            pass

    def __repr__(self):
        return '<FileSystemUploader "%s" secret=%s>' % (self.upload_to, self.secret)
