# -*- coding: utf-8 -*-
import pytest

from solution.forms import fields as f


def test_html_attrs():
    field = f.Field()
    expected = u'class="myclass" data-id="1" id="text1" checked'
    result = field._get_html_attrs(id='text1', classes='myclass', data_id=1,
        checked=True)
    print result
    assert result == expected

