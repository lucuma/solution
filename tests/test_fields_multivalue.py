# -*- coding: utf-8 -*-
from operator import eq

import solution as f


to_unicode = f._compat.to_unicode


def lists_are_equal(l1, l2):
    return all(map(eq, l1, l2))


def test_render_collection():
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


def test_render_select():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'),
             (6, u'F'), (7, u'G')]
    field = f.Select(items=items)
    field.name = 'abc'
    field.load_data(obj_value=3)

    assert field() == field.as_select()
    expected = (
        '<select foo="bar" name="abc">\n'
        '<option value="1">A</option>\n'
        '<option value="2">B</option>\n'
        '<option value="3" selected>C</option>\n'
        '<option value="4">D</option>\n'
        '<option value="5">E</option>\n'
        '<option value="6">F</option>\n'
        '<option value="7">G</option>\n'
        '</select>'
    )
    assert field(foo='bar') == expected

    field.load_data(u'3')
    assert field(foo='bar') == expected

    field = f.Select(items=items, validate=[f.Required])
    field.name = 'abc'
    assert field().startswith(u'<select name="abc" required>')


def test_render_select_groups():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    field = f.Select(items=[items1, items2, (7, u'G')])
    field.name = 'abc'
    field.load_data(obj_value=3)

    expected = (
        '<select name="abc">\n'
        '<optgroup label="First group">\n'
        '<option value="1">A</option>\n'
        '<option value="2">B</option>\n'
        '<option value="3" selected>C</option>\n'
        '</optgroup>\n'
        '<optgroup>\n'
        '<option value="4">D</option>\n'
        '<option value="5">E</option>\n'
        '<option value="6">F</option>\n'
        '</optgroup>\n'
        '<option value="7">G</option>\n'
        '</select>'
    )
    assert field.as_select() == expected


def test_render_select_as_radios():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.Select(items=items)
    field.name = 'abc'
    field.load_data(obj_value=3)

    assert field() == field.as_radios()

    expected = (
        '<label><input foo="bar" name="abc" type="radio" value="1"> A</label>\n'
        '<label><input foo="bar" name="abc" type="radio" value="2"> B</label>\n'
        '<label><input foo="bar" name="abc" type="radio" value="3" checked> C</label>'
    )
    assert field.as_radios(foo='bar') == expected


def test_render_select_as_radios_custom():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.Select(items=items)
    field.name = 'abc'
    field.load_data(obj_value=3)

    tmpl = u'<label>{label}</label><input {attrs}>'
    expected = (
        u'<label>A</label><input foo="bar" name="abc" type="radio" value="1">\n'
        u'<label>B</label><input foo="bar" name="abc" type="radio" value="2">\n'
        u'<label>C</label><input foo="bar" name="abc" type="radio" value="3" checked>'
    )
    assert field.as_radios(tmpl=tmpl, foo='bar') == expected


def test_render_select_as_radios_group():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    field = f.Select(items=[items1, items2, (7, u'G')])
    field.name = 'abc'
    field.load_data(obj_value=3)

    expected = (
        '<fieldset>\n'
        '<legend>First group</legend>\n'
        '<label><input name="abc" type="radio" value="1"> A</label>\n'
        '<label><input name="abc" type="radio" value="2"> B</label>\n'
        '<label><input name="abc" type="radio" value="3" checked> C</label>\n'
        '</fieldset>\n'
        '<fieldset>\n'
        '<label><input name="abc" type="radio" value="4"> D</label>\n'
        '<label><input name="abc" type="radio" value="5"> E</label>\n'
        '<label><input name="abc" type="radio" value="6"> F</label>\n'
        '</fieldset>\n'
        '<label><input name="abc" type="radio" value="7"> G</label>'
    )
    assert field.as_radios() == expected


def test_iterate_select():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.Select(items=items)
    assert u'|'.join([item[1] for item in field]) == 'A|B|C'


def test_validate_select():
    items = [(u'1', u'A'), (u'2', u'B'), (u'3', u'C')]
    field = f.Select(items=items, validate=[f.Required])
    field.name = 'abc'

    field.load_data(u'2')
    assert field.validate() == u'2'

    field.load_data()
    assert field.validate() is None
    assert field.error

    field.load_data(u'xxx')
    assert field.validate() is None
    assert field.error


def test_validate_select_with_type():
    items = [(u'1', u'A'), (u'2', u'B'), (u'3', u'C')]
    field = f.Select(items=items, validate=[f.Required], type=int)
    field.name = 'abc'

    field.load_data(u'2')
    assert field.validate() == 2


def test_render_multiselect():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'),
             (6, u'F'), (7, u'G')]
    field = f.MultiSelect(items=items)
    field.name = 'abc'
    field.load_data(str_value=[], obj_value=[2, 4, 6])

    assert field() == field.as_select()
    expected = (
        '<select foo="bar" name="abc">\n'
        '<option value="1">A</option>\n'
        '<option value="2" selected>B</option>\n'
        '<option value="3">C</option>\n'
        '<option value="4" selected>D</option>\n'
        '<option value="5">E</option>\n'
        '<option value="6" selected>F</option>\n'
        '<option value="7">G</option>\n'
        '</select>'
    )
    assert field(foo='bar') == expected

    field.load_data([u'2', u'4', u'6'])
    assert field(foo='bar') == expected

    field = f.MultiSelect(items=items, validate=[f.Required])
    field.name = 'abc'
    assert field().startswith(u'<select name="abc" required>')


def test_render_multiselect_groups():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    field = f.MultiSelect(items=[items1, items2, (7, u'G')])
    field.name = 'abc'
    field.load_data(str_value=[], obj_value=[2, 4, 6])
    expected = (
        '<select name="abc">\n'
        '<optgroup label="First group">\n'
        '<option value="1">A</option>\n'
        '<option value="2" selected>B</option>\n'
        '<option value="3">C</option>\n'
        '</optgroup>\n'
        '<optgroup>\n'
        '<option value="4" selected>D</option>\n'
        '<option value="5">E</option>\n'
        '<option value="6" selected>F</option>\n'
        '</optgroup>\n'
        '<option value="7">G</option>\n'
        '</select>'
    )
    assert field.as_select() == expected


def test_render_multiselect_as_checks():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.MultiSelect(items=items)
    field.name = 'abc'
    field.load_data(obj_value=[1, 2])

    assert field() == field.as_checks()

    expected = (
        '<label><input foo="bar" name="abc" type="checkbox" value="1" checked> A</label>\n'
        '<label><input foo="bar" name="abc" type="checkbox" value="2" checked> B</label>\n'
        '<label><input foo="bar" name="abc" type="checkbox" value="3"> C</label>'
    )
    assert field.as_checks(foo='bar') == expected


def test_render_multiselect_as_checks_custom():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.MultiSelect(items=items)
    field.name = 'abc'
    field.load_data(obj_value=[1, 2])

    tmpl = '<label>{label}</label><input {attrs}>'
    expected = (
        '<label>A</label><input foo="bar" name="abc" type="checkbox" value="1" checked>\n'
        '<label>B</label><input foo="bar" name="abc" type="checkbox" value="2" checked>\n'
        '<label>C</label><input foo="bar" name="abc" type="checkbox" value="3">'
    )
    assert field.as_checks(tmpl=tmpl, foo='bar') == expected


def test_render_select_as_checks_group():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    field = f.MultiSelect(items=[items1, items2, (7, u'G')])
    field.name = 'abc'
    field.load_data(obj_value=[1, 3])

    expected = (
        '<fieldset>\n'
        '<legend>First group</legend>\n'
        '<label><input name="abc" type="checkbox" value="1" checked> A</label>\n'
        '<label><input name="abc" type="checkbox" value="2"> B</label>\n'
        '<label><input name="abc" type="checkbox" value="3" checked> C</label>\n'
        '</fieldset>\n'
        '<fieldset>\n'
        '<label><input name="abc" type="checkbox" value="4"> D</label>\n'
        '<label><input name="abc" type="checkbox" value="5"> E</label>\n'
        '<label><input name="abc" type="checkbox" value="6"> F</label>\n'
        '</fieldset>\n'
        '<label><input name="abc" type="checkbox" value="7"> G</label>'
    )
    assert field.as_checks() == expected


def test_validate_multiselect():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.MultiSelect(items=items, validate=[f.Required])
    field.name = 'abc'

    field.load_data([u'2'])
    assert lists_are_equal(field.validate(), [u'2'])

    field.load_data([u'2', u'x', u'3'])
    assert lists_are_equal(field.validate(), [u'2', u'3'])

    field.load_data()
    assert field.validate() is None
    assert field.error

    field.load_data([u'xxx'])
    assert field.validate() is None
    assert field.error

