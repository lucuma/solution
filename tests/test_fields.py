# -*- coding: utf-8 -*-
import pytest

from solution.forms import fields as f
from solution.forms import validators as v


def test_html_attrs():
    field = f.Field()
    expected = u'class="myclass" data-id="1" id="text1" checked'
    attrs = {'id':'text1', 'classes':'myclass', 'data_id':1, 'checked':True}
    result = field._get_html_attrs(attrs)
    print result
    assert result == expected
    assert field._get_html_attrs() == u''


def test_validate():
    field = f.Email()
    email = u'foo@bar.com'
    field.load_value(email)
    value = field.validate()
    assert not field.error
    assert value == email

    field.value = 'lalala'
    value = field.validate()
    assert field.error


def test_hide_value():
    field = f.Password(hide_value=True)
    passw = u'qwertyuiop'
    field.load_value(passw)
    assert field.value == u''
    assert field._value == passw
    assert field.validate() == passw


def test_select_field():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'),]
    field = f.Select(items=items)
    assert field.get_items() == items

    get_items = lambda: items
    field = f.Select(items=get_items)
    assert field.get_items() == items


def test_select_field_widget():
    items = list(enumerate([chr(x) for x in range(97, 100)]))
    field = f.Select(items=items)
    assert field() == field.as_radiobuttons()

    items = list(enumerate([chr(x) for x in range(97, 120)]))
    field = f.Select(items=items)
    assert field() == field.as_select()


def test_select_field_radiobuttons():
    items = [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'),]
    field = f.Select(items=items)
    field.name = 'x'
    field.value = '3'
    expected = '''<label><input name="x" type="radio" value="1"> A</label>
<label><input name="x" type="radio" value="2"> B</label>
<label><input name="x" type="radio" value="3" checked> C</label>
<label><input name="x" type="radio" value="4"> D</label>'''
    result = field.as_radiobuttons()
    print result
    assert result == expected


def test_select_field_select():
    items = [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'),]
    field = f.Select(items=items)
    field.name = 'x'
    field.value = '3'
    expected = '''<select name="x">
<option value="1">A</option>
<option value="2">B</option>
<option value="3" selected>C</option>
<option value="4">D</option>
</select>'''
    result = field.as_select()
    print result
    assert result == expected


def test_select_multi_field():
    items = [(1, u'A'), (2, u'B'), (3, u'C'), (4, u'D'),]
    field = f.SelectMulti(items=items)
    assert field.get_items() == items

    get_items = lambda: items
    field = f.SelectMulti(items=get_items)
    assert field.get_items() == items


def test_select_multi_field_widget():
    items = list(enumerate([chr(x) for x in range(97, 100)]))
    field = f.SelectMulti(items=items)
    assert field() == field.as_checkboxes()

    items = list(enumerate([chr(x) for x in range(97, 120)]))
    field = f.SelectMulti(items=items)
    assert field() == field.as_select()


def test_select_multi_field_checkboxes():
    items = [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'),]
    field = f.SelectMulti(items=items)
    field.name = 'x'
    field.value = ['1', '3']
    expected = '''<label><input name="x" type="checkbox" value="1" checked> A</label>
<label><input name="x" type="checkbox" value="2"> B</label>
<label><input name="x" type="checkbox" value="3" checked> C</label>
<label><input name="x" type="checkbox" value="4"> D</label>'''
    result = field.as_checkboxes()
    print result
    assert result == expected


def test_select_multi_field_select():
    items = [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'),]
    field = f.SelectMulti(items=items)
    field.name = 'x'
    field.value = ['1', '3']
    expected = '''<select name="x" multiple>
<option value="1" selected>A</option>
<option value="2">B</option>
<option value="3" selected>C</option>
<option value="4">D</option>
</select>'''
    result = field.as_select()
    print result
    assert result == expected


def test_collection_field():
    field = f.Collection()
    data = '1, 2, c, 3, 4'
    field.load_value(data.split(', '))
    assert field.value == data
    assert field._value == data.split(', ')


def test_collection_field_filters():
    field = f.Collection(filters=[v.IsNumber])
    data = '1, 2, c, 3, 4'.split(', ')
    field.load_value(data)
    result = field.validate()
    assert result == ['1', '2', '3', '4']

    field = f.Collection(filters=[v.IsNumber()])
    field.load_value(data)
    result = field.validate()
    assert result == ['1', '2', '3', '4']

    field = f.Collection(filters=[v.ValidEmail])
    field.load_value(data)
    result = field.validate()
    assert result == []


def test_collection_field_clean():
    field = f.Collection(clean=int)
    data = '1, 2, c, 3, 4'.split(', ')
    field.load_value(data)
    result = field.validate()
    assert result == [1, 2, 3, 4]

    # Test filters + clean
    field = f.Collection(filters=[v.IsNumber], clean=int)
    field.load_value(data)
    result = field.validate()
    assert result == [1, 2, 3, 4]

