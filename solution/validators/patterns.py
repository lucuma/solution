# coding=utf-8
from email.utils import parseaddr
import re

from .._compat import string_types, urlsplit, urlunsplit, to_unicode

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

    def __init__(self, regex, message=None, flags=re.IGNORECASE):
        if isinstance(regex, string_types):
            regex = re.compile(regex, flags)
        self.regex = regex
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        return self.regex.match(py_value or u'')


class ValidColor(Match):
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

IsColor = ValidColor


class ValidEmail(Validator):
    """Validates an email address.

    Note that the purpose of this validator is to alert the user of a typing
    mistake, so it uses a very permissive regexp. Even if the format is valid,
    it cannot guarantee that the email is real.

    :param message:
        Error message to raise in case of a validation error.

    """
    message = u'Enter a valid e-mail address.'

    email_rx = re.compile(
        r'^[A-Z0-9][A-Z0-9._%+-]*@[A-Z0-9][A-Z0-9\-\.]{0,61}\.[A-Z0-9]+$',
        re.IGNORECASE)

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def __call__(self, py_value=None, form=None):
        if not py_value or '@' not in py_value:
            return False
        py_value = parseaddr(py_value)[-1]
        if '.@' in py_value:
            return False
        try:
            py_value = self._encode_idna(py_value)
        except (UnicodeDecodeError, UnicodeError):
            return False
        return bool(self.email_rx.match(py_value))

    def _encode_idna(self, py_value):
        parts = py_value.split(u'@')
        domain = parts[-1]
        domain = domain.encode(u'idna')
        parts[-1] = to_unicode(domain)
        return u'@'.join(parts)


class ValidURL(Validator):
    """Simple regexp based URL validation. Much like the IsEmail validator, you
    probably want to validate the URL later by other means if the URL must
    resolve.

    :param message:
        Error message to raise in case of a validation error.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.

    """
    message = u'Enter a valid URL.'
    url_rx = r'^([a-z]{3,7}:(//)?)?([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$'

    def __init__(self, message=None, require_tld=True):
        tld_part = r'\.[a-z]{2,10}' if require_tld else u''
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
        except (UnicodeDecodeError, UnicodeError):
            return False
        return False

    def _encode_idna(self, py_value):
        scheme, netloc, path, query, fragment = urlsplit(py_value)
        netloc = netloc.encode('idna')  # IDN -> ACE
        return urlunsplit((scheme, netloc, path, query, fragment))
