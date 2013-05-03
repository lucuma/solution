# -*- coding: utf-8 -*-
from datetime import date, datetime
from decimal import Decimal

import pytest
import solution as f


def test_field():
    field = f.Field()
    value = u'abc'
    field.load_data(value)
    assert field.to_string() == value
    assert field.validate() == value


def test_reset():
    field = f.Field()
    field.load_data('a', 'b', 'c')
    assert (field.str_value and field.obj_value and field.file_data and
            not field.empty)
    field.reset()
    assert not (field.str_value or field.obj_value or field.file_data or
                not field.empty)


def test_field_helpers():
    field = f.Field()

    assert (field.label_tag(u'Something', classes=u'span2') ==
            u'<label class="span2">Something</label>')

    assert field.error_tag(classes=u'alert alert-error') == u''

    field.error = f.ValidationError(u'Error message')
    assert (field.error_tag(classes=u'alert alert-error') ==
            u'<div class="alert alert-error">Error message</div>')


def test_validate():
    field = f.Field(default=u'default value')
    field.validate()
    assert field.validate() == u'default value'
    assert not field.error

    field = f.Field(validate=[f.Required])
    assert field.validate() is None
    assert field.error.message


def test_validate_with_custom_msg():
    field = f.Field(validate=[f.ValidEmail(u'invalid')])
    field.load_data('email')
    field.validate()
    assert field.error.message == u'invalid'


def test_render_text():
    field = f.Text()
    field.name = u'abc'
    field.load_data(u'123')

    assert unicode(field) == field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="text" value="123">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">123</textarea>')
    assert (field(foo='bar', type='email') ==
            u'<input foo="bar" name="abc" type="email" value="123">')

    field = f.Text(hide_value=True)
    field.name = u'abc'
    field.load_data(u'123')
    assert (field(foo='bar', type='password') ==
            u'<input foo="bar" name="abc" type="password" value="">')


def test_validate_text():
    field = f.Text(validate=[f.Required])
    field.name = u'abc'
    field.load_data(u'123')
    assert field.validate() == u'123'

    field = f.Text(hide_value=True, validate=[f.Required])
    field.name = u'abc'
    field.load_data(u'123')
    assert field.validate() == u'123'


def test_render_number():
    field = f.Number()
    field.name = u'abc'
    field.load_data('123')
    assert unicode(field) == field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="number" value="123">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">123</textarea>')
    assert (field(foo='bar', type='score') ==
            u'<input foo="bar" name="abc" type="score" value="123">')

    field = f.Number(validate=[f.Required])
    field.name = u'abc'
    field.load_data('123')
    assert (field() ==
            u'<input name="abc" type="number" value="123" required>')
    assert (field(required=False) == 
            u'<input name="abc" type="number" value="123">')


def test_validate_number():
    field = f.Number(validate=[f.Required])
    field.name = u'abc'
    
    field.load_data('123')
    assert field.validate() == 123

    field.load_data('defg')
    assert not field.validate()
    assert field.error


def test_number_types():
    for t in (int, float, Decimal):
        field = f.Number(type=t)
        field.load_data('3.02')
        assert field.validate() == t(float('3.02'))


def test_render_color():
    field = f.Color()
    field.name = u'abc'
    field.load_data('#ffaf2e')

    assert unicode(field) == field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="color" value="#ffaf2e">')
    assert (field(foo='bar', type='text') ==
            u'<input foo="bar" name="abc" type="text" value="#ffaf2e">')

    field = f.Color(validate=[f.Required])
    field.name = u'abc'
    field.load_data('#ffaf2e')
    assert (field() == 
            u'<input name="abc" type="color" value="#ffaf2e" required>')
    assert (field(required=False) == 
            u'<input name="abc" type="color" value="#ffaf2e">')


def test_validate_color():
    field = f.Color(validate=[f.Required])
    field.name = u'abc'

    field.load_data('#ffaf2e')
    assert field.validate() == '#ffaf2e'

    field.load_data('FFAF2E')
    assert field.validate() == '#ffaf2e'

    field.load_data('#fae')
    assert field.validate() == '#ffaaee'

    field.load_data('#faef')
    assert field.validate() == '#ffaaeeff'

    field.load_data('rgb(40, 104, 199)')
    assert field.validate() == '#2868c7'

    field.load_data('rgba(14,98,13,.5)')
    assert field.validate() == '#0e620d80'

    field.load_data()
    assert not field.validate()
    assert field.error

    field.load_data('not a color')
    assert not field.validate()
    assert field.error

    field.load_data('#ffaf2')
    assert not field.validate()
    assert field.error

    field.load_data('rgb(300, 300, 300)')
    assert not field.validate()
    assert field.error

    field.load_data('rgba(0, 0, 0, 2)')
    assert not field.validate()
    assert field.error


def test_render_boolean():
    field = f.Boolean()
    field.name = u'abc'

    field.load_data(obj_value=True)
    assert unicode(field) == field() == field.as_checkbox()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="checkbox" checked>')

    field.load_data(obj_value=False)
    assert field() == u'<input name="abc" type="checkbox">'

    field.load_data(u'no')
    assert field() == u'<input name="abc" type="checkbox">'

    field = f.Boolean(validate=[f.Required])
    field.name = u'abc'
    field.load_data()
    assert field() == u'<input name="abc" type="checkbox" required>'
    assert field(required=False) == u'<input name="abc" type="checkbox">'


def test_validate_boolean():
    field = f.Boolean(validate=[f.Required])
    field.name = u'abc'

    for val in [u'', u'0', u'no', u'off', u'false', u'NO', 'fAlsE']:
        field.load_data(val)
        assert field.validate() == False

    for val in [u'yes', u'1', u'ok', u'Of course!!!1', u'whatever']:
        field.load_data(val)
        assert field.validate() == True

    field.load_data()
    assert field.validate() is None
    assert field.error


def test_render_file():
    field = f.File()
    field.name = u'abc'

    assert unicode(field) == field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="file">')

    field = f.File(validate=[f.Required])
    field.name = u'abc'
    assert (field() ==
            u'<input name="abc" type="file" required>')
    assert (field(required=False) ==
            u'<input name="abc" type="file">')


def test_file_validate_calls_upload():
    called = []
    def upload(data):
        called.append(data)

    field = f.File(upload=upload)
    field.name = u'abc'
    field.load_data(file_data='data')

    field.validate()
    assert called[0] == 'data'


def test_file_upload_error_make_validation_fail():
    called = []
    def upload(data):
        raise f.ValidationError('test')

    field = f.File(upload=upload)
    field.name = u'abc'
    field.load_data(file_data='data')

    assert field.validate() is None
    assert field.error.message == 'test'


def test_validate_file():
    field = f.File()
    field.name = u'abc'

    field.load_data(obj_value=u'obj value')
    assert field.validate() == u'obj value'
    assert not field.error

    field.load_data(obj_value=u'obj value', file_data=u'file data')
    assert field.validate() == u'file data'
    assert not field.error

