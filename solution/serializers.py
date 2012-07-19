# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
from decimal import Decimal
# Get the fastest json available
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError('Unable to find a JSON implementation')
import types


def to_json(value, **options):
    options.setdefault('cls', JSONEncoder)
    options.setdefault('sort_keys', True)
    return json.dumps(value, **options)


def from_json(value, **options):
    options.setdefault('object_hook', json_decoder)
    return json.loads(value, **options)


#------------------------------------------------------------------------------


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATETIME_FORMAT)
        elif isinstance(obj, datetime.date):
            return obj.strftime(DATE_FORMAT)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)


def json_decoder(d):
    if isinstance(d, list):
        pairs = enumerate(d)
    elif isinstance(d, dict):
        pairs = d.items()
    result = []
    for k, v in pairs:
        if isinstance(v, basestring):
            try:
                v = datetime.datetime.strptime(v, DATETIME_FORMAT)
            except ValueError:
                try:
                    v = datetime.datetime.strptime(v, DATE_FORMAT).date()
                except ValueError:
                    pass
        elif isinstance(v, (dict, list)):
            v = json_decoder(v)
        result.append((k, v))
    if isinstance(d, list):
        return [x[1] for x in result]
    elif isinstance(d, dict):
        return dict(result)


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_unicode(strings_only=True).
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def to_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a unicode object representing 's'. Treats bytestrings using the
    `encoding` codec.

    If strings_only is True, don't convert (some) non-string-like objects.

    --------------------------------
    Copied almost unchanged from Django <https://www.djangoproject.com/>
    Copyright © Django Software Foundation and individual contributors.
    Used under the modified BSD license.
    """
    # Handle the common case first, saves 30-40% in performance when s
    # is an instance of unicode.
    if isinstance(s, unicode):
        return s
    if strings_only and is_protected_type(s):
        return s
    encoding = encoding or 'utf-8'
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = u' '.join([to_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = u' '.join([to_unicode(arg, encoding, strings_only,
                errors) for arg in s])
    return s

