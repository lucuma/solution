# -*- coding: utf-8 -*-
from email.utils import parseaddr
import re
import urlparse

from ..utils import to_unicode
from .validator import Validator


class Match(Validator):
    """Validates the field against a regular expression.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.

    :param flags:
        The regexp flags to use. By default re.IGNORECASE.
        Ignored if `regex` is not a string.

    :param message:
        Error message to raise in case of a validation error.
    
    """
    message = u'This value doesn\'t seem to be valid.'

    def __init__(self, regex, flags=re.IGNORECASE, message=None):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        return self.regex.match(py_value or u'')


class IsColor(Match):
    """Validates that the field is a string representing a rgb or rgba color
    in the format `#rrggbb[aa]`.

    :param message:
        Error message to raise in case of a validation error.
    """
    message = u'Enter a valid color.'

    regex = re.compile(r'#[0-9a-f]{6,8}', re.IGNORECASE)

    def __init__(self, message=None):
        if message is not None:
            self.message = message


class ValidEmail(Validator):
    """Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, or wen it doesn't matters very much the email is real.

    :param message:
        Error message to raise in case of a validation error.

    """
    message = u'Enter a valid e-mail address.'

    email_rx = re.compile(
        r'''(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*'''  # dot-atom
        r'''|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"''' # quoted-string
        r''')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$''',
        re.IGNORECASE)

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        if not py_value:
            return False
        _, py_value = parseaddr(py_value)
        if self.email_rx.match(py_value):
            return True
        # Common case failed. Try for possible IDN domain-part
        try:
            if py_value and u'@' in py_value:
                py_value = self._encode_idna(py_value)
            return bool(self.email_rx.match(py_value))
        except UnicodeDecodeError:
            pass
        return False

    def _encode_idna(self, py_value):
        parts = py_value.split(u'@')
        domain_part = parts[-1]
        parts[-1] = parts[-1].encode('idna')
        return u'@'.join(parts)


class ValidURL(Validator):
    """Simple regexp based URL validation. Much like the IsEmail validator, you
    probably want to validate the URL later by other means if the URL must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.

    :param message:
        Error message to raise in case of a validation error.

    """
    message = u'Enter a valid URL.'
    url_rx = ur'^([a-z]{3,7}:(//)?)?([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$'

    def __init__(self, require_tld=True, message=None):
        tld_part = ur'\.[a-z]{2,10}' if require_tld else u''
        self.regex = re.compile(self.url_rx % tld_part, re.IGNORECASE)
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        if not py_value:
            return False
        if self.regex.match(py_value):
            return True
        # Common case failed. Try for possible IDN domain-part
        try:
            py_value = self._encode_idna(py_value)
            return bool(self.regex.match(py_value))
        except UnicodeDecodeError:
            pass
        return False

    def _encode_idna(self, py_value):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(py_value)
        netloc = netloc.encode('idna') # IDN -> ACE
        return urlparse.urlunsplit((scheme, netloc, path, query, fragment))

