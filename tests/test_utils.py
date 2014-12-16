# coding=utf-8
from __future__ import print_function
from solution import utils


def test_html_attrs():
    expected = u'class="myclass" data-id="1" id="text1" checked'
    attrs = {'id': 'text1', 'classes': 'myclass', 'data_id': 1, 'checked': True}
    result = utils.get_html_attrs(attrs)
    print(result)
    assert result == expected
    assert utils.get_html_attrs() == u''

