# coding=utf-8
from operator import eq

import solution as f


def _clean(form, value, **kwargs):
    return value


def lists_are_equal(l1, l2):
    return all(map(eq, l1, l2))


def test_load_data():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'), (6, u'F'), (7, u'G')]
    user_value = [u'1', u'2', u'3']
    obj_value = [2, 4, 6]

    field = f.MultiSelect(items=items)
    field.load_data()
    assert field.validate() == []

    field = f.MultiSelect(items=items)
    field.load_data(user_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items)
    field.load_data(user_value, obj_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items, validate=[f.Required])
    field.load_data(user_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items, validate=[f.Required])
    field.load_data(user_value, obj_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items)
    field.load_data(None, obj_value)
    assert field.validate() == obj_value


def test_load_data_with_default():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'), (6, u'F'), (7, u'G')]
    default = [5]
    user_value = [u'1', u'2', u'3']
    obj_value = [2, 4, 6]

    field = f.MultiSelect(items=items, default=default)
    field.load_data()
    assert field.validate() == default

    field = f.MultiSelect(items=items, default=default)
    field.load_data(user_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items, default=default)
    field.load_data(user_value, obj_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items, default=default, validate=[f.Required])
    field.load_data(user_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items, default=default, validate=[f.Required])
    field.load_data(user_value, obj_value)
    assert field.validate() == user_value

    field = f.MultiSelect(items=items, default=default)
    field.load_data(None, obj_value)
    assert field.validate() == obj_value


def test_render_multiselect():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'),
             (6, u'F'), (7, u'G')]
    field = f.MultiSelect(items=items)
    field.name = 'abc'
    field.load_data(str_value=[], obj_value=[2, 4, 6])

    assert field() == field.as_select()
    expected = (
        '<select foo="bar" name="abc" multiple>\n'
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
    assert field().startswith(u'<select name="abc" required multiple>')


def test_render_multiselect_extra():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'),
             (6, u'F'), (7, u'G')]
    field = f.MultiSelect(items=items, data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = 'abc'
    field.load_data(str_value=[], obj_value=[2, 4, 6])

    assert field() == field.as_select()
    expected = (
        '<select aria-label="test" foo="bar" name="abc" data-modal multiple>\n'
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


def test_render_multiselect_groups():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    field = f.MultiSelect(items=[items1, items2, (7, u'G')])
    field.name = 'abc'
    field.load_data(str_value=[], obj_value=[2, 4, 6])
    expected = (
        '<select name="abc" multiple>\n'
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


def test_render_multiselect_as_checks_extra():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.MultiSelect(items=items, data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = 'abc'
    field.load_data(obj_value=[1, 2])

    assert field() == field.as_checks()

    expected = (
        '<label><input aria-label="test" foo="bar" name="abc" type="checkbox" value="1" checked data-modal> A</label>\n'
        '<label><input aria-label="test" foo="bar" name="abc" type="checkbox" value="2" checked data-modal> B</label>\n'
        '<label><input aria-label="test" foo="bar" name="abc" type="checkbox" value="3" data-modal> C</label>'
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


def test_render_multiselect_as_checks_group():
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


def test_render_multiselect_default_value():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'),
             (6, u'F'), (7, u'G')]
    field = f.MultiSelect(items=items, default=[4, 6])
    field.name = 'abc'
    field.load_data(str_value=[], obj_value=[])

    expected = (
        '<select name="abc" multiple>\n'
        '<option value="1">A</option>\n'
        '<option value="2">B</option>\n'
        '<option value="3">C</option>\n'
        '<option value="4" selected>D</option>\n'
        '<option value="5">E</option>\n'
        '<option value="6" selected>F</option>\n'
        '<option value="7">G</option>\n'
        '</select>'
    )
    assert field.as_select() == expected


def test_multiselect_as_dict():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'Curaçao'),
             (6, u'F'), (7, u'G'), (8, 'Curaçao')]
    field = f.MultiSelect(items=items)
    field.name = u'abc'

    expdict = {
        'name': u'abc',
        'items': items,
        'value': [],
        'error': '',
    }
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected

    field.load_data([u'2', u'3'])
    expdict['value'] = [u'2', u'3']
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
