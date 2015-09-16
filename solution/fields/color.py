# coding=utf-8
import re

from .. import validators as v
from .text import Text


class Color(Text):

    """A color field.

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

    :param hide_value:
        Do not render the current value a a string. Useful with passwords
        fields.

    """
    _type = 'color'
    default_validator = v.IsColor

    rx_colors = re.compile(
        r'#?(?P<hex>[0-9a-f]{3,8})|'
        r'rgba?\((?P<r>[0-9]+)\s*,\s*(?P<g>[0-9]+)\s*,\s*(?P<b>[0-9]+)'
        r'(?:\s*,\s*(?P<a>\.?[0-9]+))?\)',
        re.IGNORECASE)

    def str_to_py(self, **kwargs):
        if not self.str_value:
            return None
        str_value = self.str_value.strip().replace(' ', '').lower()
        m = self.rx_colors.match(str_value)
        if not m:
            return None
        md = m.groupdict()
        if md['hex']:
            return normalize_hex(md['hex'])
        return normalize_rgb(md['r'], md['g'], md['b'], md.get('a'))


def normalize_hex(hex_color):
    """Transform a xxx hex color to xxxxxx.
    """
    hex_color = hex_color.replace('#', '').lower()
    length = len(hex_color)
    if length in (6, 8):
        return '#' + hex_color
    if length not in (3, 4):
        return None
    strhex = u'#%s%s%s' % (
        hex_color[0] * 2,
        hex_color[1] * 2,
        hex_color[2] * 2)
    if length == 4:
        strhex += hex_color[3] * 2
    return strhex


def normalize_rgb(r, g, b, a):
    """Transform a rgb[a] color to #hex[a].
    """
    r = int(r, 10)
    g = int(g, 10)
    b = int(b, 10)
    if a:
        a = float(a) * 256
    if r > 255 or g > 255 or b > 255 or (a and a > 255):
        return None
    color = '#%02x%02x%02x' % (r, g, b)
    if a:
        color += '%02x' % a
    return color
