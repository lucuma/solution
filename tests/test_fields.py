# -*- coding: utf-8 -*-
import pytest

from solution import forms as f


def test_html_attrs():
    field = f._Field()
    expected = u'class="myclass" data-id="1" id="text1" checked'
    attrs = {'id':'text1', 'classes':'myclass', 'data_id':1, 'checked':True}
    result = field._get_html_attrs(attrs)
    print result
    assert result == expected
    assert field._get_html_attrs() == u''


def test_validate():
    field = f._Field(validate=[f.ValidEmail(u'invalid')])
    field.value = 'email'
    field.validate()
    assert field.error and field.error.message == u'invalid'

    field = f._Email()
    email = u'foo@bar.com'
    field.value = email
    value = field.validate()
    assert not field.error
    assert value == email

    field.value = 'lalala'
    value = field.validate()
    assert field.error


def test_hide_value():
    field = f._Password(hide_value=True)
    passw = u'qwertyuiop'
    field.value = passw
    assert field.to_html() == u''
    assert field.validate() == passw





#- Select
#------------------------------------------------------------------------------#

def test_select_field():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'),]
    field = f._Select(items=items)
    assert field.get_items() == items

    get_items = lambda: items
    field = f._Select(items=get_items)
    assert field.get_items() == items


def test_select_field_widget():
    items = list(enumerate([chr(x) for x in range(97, 100)]))
    field = f._Select(items=items)
    assert field() == field.as_radiobuttons()

    items = list(enumerate([chr(x) for x in range(97, 120)]))
    field = f._Select(items=items)
    assert field() == field.as_select()


def test_select_field_radiobuttons():
    items = [(1, 'A'), (2, 'B'), (3, 535), (4, 'D'),]
    field = f._Select(items=items)
    field.name = 'x'
    field.value = 3
    expected = '''<label><input name="x" type="radio" value="1"> A</label>
<label><input name="x" type="radio" value="2"> B</label>
<label><input name="x" type="radio" value="3" checked> 535</label>
<label><input name="x" type="radio" value="4"> D</label>'''
    result = field.as_radiobuttons()
    print result
    assert result == expected


def test_select_field_select():
    items = [(1, 'A'), (2, 'B'), (3, 535), (4, 'D'),]
    field = f._Select(items=items)
    field.name = 'x'
    field.value = 3
    expected = '''<select name="x">
<option value="1">A</option>
<option value="2">B</option>
<option value="3" selected>535</option>
<option value="4">D</option>
</select>'''
    result = field.as_select()
    print result
    assert result == expected


def test_select_multi_field():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'),]
    field = f._Select(items=items, multiple=True)
    assert field.get_items() == items

    get_items = lambda: items
    field = f._Select(items=get_items, multiple=True)
    assert field.get_items() == items


def test_select_multi_field_widget():
    items = list(enumerate([chr(x) for x in range(97, 100)]))
    field = f._Select(items=items, multiple=True)
    assert field() == field.as_checkboxes()

    items = list(enumerate([chr(x) for x in range(97, 120)]))
    field = f._Select(items=items, multiple=True)
    assert field() == field.as_select()


def test_select_multi_field_checkboxes():
    items = [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'),]
    field = f._Select(items=items, multiple=True)
    field.name = 'x'
    field.value = [1, 3]
    expected = '''<label><input name="x" type="checkbox" value="1" checked> A</label>
<label><input name="x" type="checkbox" value="2"> B</label>
<label><input name="x" type="checkbox" value="3" checked> C</label>
<label><input name="x" type="checkbox" value="4"> D</label>'''
    result = field.as_checkboxes()
    print result
    assert result == expected


def test_select_multi_field_select():
    items = [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'),]
    field = f._Select(items=items, multiple=True)
    field.name = 'x'
    field.value = [1, 3]
    expected = '''<select name="x" multiple>
<option value="1" selected>A</option>
<option value="2">B</option>
<option value="3" selected>C</option>
<option value="4">D</option>
</select>'''
    result = field.as_select()
    print result
    assert result == expected


#- Collection
#------------------------------------------------------------------------------#

def test_collection_field():
    field = f._Collection()
    data = '1, 2, c, 3, 4'
    field.value = data
    assert field.to_python() == data.split(', ')


def test_collection_field_filters():
    field = f._Collection(filters=[f.IsNumber])
    data = '1, 2, c, 3, 4'.split(', ')
    field.value = data
    result = field.validate()
    assert result == ['1', '2', '3', '4']

    field = f._Collection(filters=[f.IsNumber()])
    field.value = data
    result = field.validate()
    assert result == ['1', '2', '3', '4']

    field = f._Collection(filters=[f.ValidEmail])
    field.value = data
    result = field.validate()
    assert result == []


def test_collection_field_clean():
    def to_number(value, *args, **kwargs):
        return int(value)

    field = f._Collection(clean=to_number)
    data = '1, 2, c, 3, 4'.split(', ')
    field.value = data
    result = field.validate()
    assert result == [1, 2, 3, 4]

    # Test filters + clean
    field = f._Collection(filters=[f.IsNumber], clean=to_number)
    field.value = data
    result = field.validate()
    assert result == [1, 2, 3, 4]

