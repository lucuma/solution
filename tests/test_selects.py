# coding=utf-8
import solution as f


def _clean(form, value, **kwargs):
    return value


def test_render_select():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'Curaçao'),
             (6, u'F'), (7, u'G'), (8, 'Curaçao')]
    field = f.Select(items=items)
    field.name = 'abc'
    field.load_data(obj_value=3)

    assert field() == field.as_select()
    expected = (
        u'<select foo="bar" name="abc">\n'
        u'<option value="1">A</option>\n'
        u'<option value="2">B</option>\n'
        u'<option value="3" selected>C</option>\n'
        u'<option value="4">D</option>\n'
        u'<option value="5">Curaçao</option>\n'
        u'<option value="6">F</option>\n'
        u'<option value="7">G</option>\n'
        u'<option value="8">Curaçao</option>\n'
        u'</select>'
    )
    assert field(foo='bar') == expected

    field.load_data(u'3')
    assert field(foo='bar') == expected

    field = f.Select(items=items, validate=[f.Required])
    field.name = 'abc'
    assert field().startswith(u'<select name="abc" required>')


def test_render_select_extra():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'Curaçao'),
             (6, u'F'), (7, u'G'), (8, 'Curaçao')]
    field = f.Select(items=items, data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = 'abc'
    field.load_data(obj_value=3)

    assert field() == field.as_select()
    expected = (
        u'<select aria-label="test" foo="bar" name="abc" data-modal>\n'
        u'<option value="1">A</option>\n'
        u'<option value="2">B</option>\n'
        u'<option value="3" selected>C</option>\n'
        u'<option value="4">D</option>\n'
        u'<option value="5">Curaçao</option>\n'
        u'<option value="6">F</option>\n'
        u'<option value="7">G</option>\n'
        u'<option value="8">Curaçao</option>\n'
        u'</select>'
    )
    assert field(foo='bar') == expected


def test_render_select_groups():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    items = [items1, items2, (7, u'G')]
    field = f.Select(items=items)
    field.name = 'abc'
    field.load_data(obj_value=3)

    expected = (
        u'<select name="abc">\n'
        u'<optgroup label="First group">\n'
        u'<option value="1">A</option>\n'
        u'<option value="2">B</option>\n'
        u'<option value="3" selected>C</option>\n'
        u'</optgroup>\n'
        u'<optgroup>\n'
        u'<option value="4">D</option>\n'
        u'<option value="5">E</option>\n'
        u'<option value="6">F</option>\n'
        u'</optgroup>\n'
        u'<option value="7">G</option>\n'
        u'</select>'
    )
    assert field.as_select() == expected


def test_render_select_as_radios():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.Select(items=items)
    field.name = 'abc'
    field.load_data(obj_value=3)

    assert field() == field.as_radios()

    expected = (
        u'<label><input foo="bar" name="abc" type="radio" value="1"> A</label>\n'
        u'<label><input foo="bar" name="abc" type="radio" value="2"> B</label>\n'
        u'<label><input foo="bar" name="abc" type="radio" value="3" checked> C</label>'
    )
    assert field.as_radios(foo='bar') == expected


def test_render_select_as_radios_extra():
    items = [(1, u'A'), (2, u'B'), (3, u'C')]
    field = f.Select(items=items, data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = 'abc'
    field.load_data(obj_value=3)

    assert field() == field.as_radios()

    expected = (
        u'<label><input aria-label="test" foo="bar" name="abc" type="radio" value="1" data-modal> A</label>\n'
        u'<label><input aria-label="test" foo="bar" name="abc" type="radio" value="2" data-modal> B</label>\n'
        u'<label><input aria-label="test" foo="bar" name="abc" type="radio" value="3" checked data-modal> C</label>'
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
        u'<fieldset>\n'
        u'<legend>First group</legend>\n'
        u'<label><input name="abc" type="radio" value="1"> A</label>\n'
        u'<label><input name="abc" type="radio" value="2"> B</label>\n'
        u'<label><input name="abc" type="radio" value="3" checked> C</label>\n'
        u'</fieldset>\n'
        u'<fieldset>\n'
        u'<label><input name="abc" type="radio" value="4"> D</label>\n'
        u'<label><input name="abc" type="radio" value="5"> E</label>\n'
        u'<label><input name="abc" type="radio" value="6"> F</label>\n'
        u'</fieldset>\n'
        u'<label><input name="abc" type="radio" value="7"> G</label>'
    )
    assert field.as_radios() == expected


def test_render_select_default_value():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'E'),
             (6, u'F'), (7, u'G')]
    field = f.Select(items=items, default=4)
    field.name = 'abc'
    field.load_data(value='')

    expected = (
        u'<select name="abc">\n'
        u'<option value="1">A</option>\n'
        u'<option value="2">B</option>\n'
        u'<option value="3">C</option>\n'
        u'<option value="4" selected>D</option>\n'
        u'<option value="5">E</option>\n'
        u'<option value="6">F</option>\n'
        u'<option value="7">G</option>\n'
        u'</select>'
    )
    assert field.as_select() == expected


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


def test_validate_select_with_groups():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    items = [items1, items2, (7, u'G')]
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


def test_validate_select_with_groups_and_type():
    items1 = [u'First group', (1, u'A'), (2, u'B'), (3, u'C')]
    items2 = [(4, u'D'), (5, u'E'), (6, u'F')]
    items = [items1, items2, (7, u'G')]
    field = f.Select(items=items, validate=[f.Required], type=int)
    field.name = 'abc'

    field.load_data(u'2')
    assert field.validate() == 2


def test_select_as_dict():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'), (5, u'Curaçao'),
             (6, u'F'), (7, u'G'), (8, 'Curaçao')]
    field = f.Select(items=items)
    field.name = u'abc'

    expdict = {
        'name': u'abc',
        'items': items,
        'value': u'',
        'error': '',
    }
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected

    field.load_data(obj_value=3)
    expdict['value'] = '3'
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
