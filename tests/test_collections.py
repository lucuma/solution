# coding=utf-8
from operator import eq

import solution as f


def lists_are_equal(l1, l2):
    return all(map(eq, l1, l2))


def test_render_():
    field = f.Collection()
    field.name = 'abc'
    field.load_data(u'a, b,c')

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="text" value="a, b, c">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">a, b, c</textarea>')
    assert (field(foo='bar', type='email') ==
            u'<input foo="bar" name="abc" type="email" value="a, b, c">')

    field.load_data(obj_value=[u'd', u'e', u'f'])
    assert field() == u'<input name="abc" type="text" value="d, e, f">'

    field.sep = '|'
    field.load_data(obj_value=[u'a', u'b', u'c'])
    assert field() == u'<input name="abc" type="text" value="a|b|c">'

    field = f.Collection(validate=[f.Required])
    field.name = u'abc'
    field.load_data(u'a,b')
    assert (field() ==
            u'<input name="abc" type="text" value="a, b" required>')
    assert (field(required=False) ==
            u'<input name="abc" type="text" value="a, b">')

    field = f.Collection()
    field.name = u'abc'
    field.load_data([])
    assert field() == u'<input name="abc" type="text" value="">'
    field.load_data([], [])
    assert field() == u'<input name="abc" type="text" value="">'


def test_validate_collection():
    field = f.Collection()
    field.name = 'abc'

    field.load_data(u'a, b,c  ')
    assert lists_are_equal(field.validate(), [u'a', u'b', u'c'])

    field.load_data([u'a, b'])
    assert lists_are_equal(field.validate(), [u'a', u'b'])
    field.validate() == [u'a', u'b']

    field = f.Collection(sep='|')
    field.load_data(u'a, b,c  ')
    assert lists_are_equal(field.validate(), [u'a, b,c'])


def test_filter_collection():
    def filter_the_b(py_value):
        return py_value != u'b'

    field = f.Collection(filters=[filter_the_b])
    field.name = 'abc'
    field.load_data(u'a, b,c')
    assert lists_are_equal(field.validate(), [u'a', u'c'])

    field = f.Collection(filters=[f.ValidEmail])
    field.name = 'abc'
    field.load_data([u'a@example.com,b@example.com'])
    assert field.validate() == [u'a@example.com', u'b@example.com']


def test_collection_as_dict():
    field = f.Collection()
    field.name = 'abc'

    expdict = {
        'name': u'abc',
        'value': [],
        'error': '',
    }
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected

    field.load_data(u'a, b,c')
    expdict['value'] = u'a,b,c'.split(',')
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
