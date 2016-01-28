# coding=utf-8
from __future__ import print_function
from decimal import Decimal

import solution as f


to_unicode = f._compat.to_unicode


def _clean(form, value, **kwargs):
    return value


def test_validation_error():
    v = f.ValidationError(u'olé')
    assert v.message == u'olé'

    v = f.ValidationError()
    assert v.message


def test_field():
    field = f.Field()
    value = u'abc'
    field.load_data(value)
    assert field.to_string() == value
    assert field.validate() == value


def test_field_default():
    value = u'abc'
    field = f.Field(default=value)
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
    assert str(field.error)


def test_validate_with_custom_msg():
    field = f.Field(validate=[f.ValidEmail(u'invalid')])
    field.load_data('email')
    field.validate()
    assert str(field.error) == 'invalid'


def test_clean_error_make_validation_fail():
    def clean(data):
        raise f.ValidationError('test')

    field = f.Field(clean=clean)
    field.name = u'abc'
    field.load_data('foobar')

    assert field.validate() is None
    assert str(field.error) == 'test'


def test_render_text():
    field = f.Text()
    field.name = u'abc'
    field.load_data(u'123')

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="text" value="123">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">123</textarea>')
    assert (field(foo='bar', type='email') ==
            u'<input foo="bar" name="abc" type="email" value="123">')

    field.load_data(u'"Ben" & Jerry')
    assert (field() == u'<input name="abc" type="text" value=\'"Ben" & Jerry\'>')

    field = f.Text(hide_value=True)
    field.name = u'abc'
    field.load_data(u'123')
    assert (field(foo='bar', type='password') ==
            u'<input foo="bar" name="abc" type="password" value="">')


def test_render_text_extra():
    field = f.Text(data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = u'abc'
    field.load_data(u'123')

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="text" value="123" data-modal>')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea aria-label="test" foo="bar" name="abc" data-modal>123</textarea>')
    assert (field(foo='bar', type='email') ==
            u'<input aria-label="test" foo="bar" name="abc" type="email" value="123" data-modal>')


def test_validate_text():
    field = f.Text(validate=[f.Required])
    field.name = u'abc'
    field.load_data(u'123')
    assert field.validate() == u'123'

    field = f.Text(hide_value=True, validate=[f.Required])
    field.name = u'abc'
    field.load_data(u'123')
    assert field.validate() == u'123'

    field = f.Text(validate=[f.Required])
    field.name = u'abc'

    field.load_data(u'')
    assert field.validate() is None
    assert field.error

    field.load_data(u' ')
    assert field.validate() is None
    assert field.error


def test_text_default():
    value = u'abc'
    field = f.Text(default=value)
    assert field.to_string() == value
    assert field.validate() == value


def test_render_number():
    field = f.Number()
    field.name = u'abc'
    field.load_data('123')
    assert field() == field.as_input()
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


def test_render_number_extra():
    field = f.Number(data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = u'abc'
    field.load_data('123')
    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="number" value="123" data-modal>')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea aria-label="test" foo="bar" name="abc" data-modal>123</textarea>')
    assert (field(foo='bar', type='score') ==
            u'<input aria-label="test" foo="bar" name="abc" type="score" value="123" data-modal>')


def test_validate_number():
    field = f.Number(validate=[f.Required])
    field.name = u'abc'

    field.load_data('123')
    assert field.validate() == 123

    field.load_data('defg')
    assert not field.validate()
    assert field.error


def test_number_types():
    field = f.Number(type=int)
    field.load_data('3.02')
    assert field.validate() == 3

    field = f.Number(type=float)
    field.load_data('3.02')
    assert field.validate() == float('3.02')

    field = f.Number(type=Decimal)
    field.load_data('3.02')
    assert field.validate() == Decimal('3.02')


def test_number_default():
    field = f.Number(default=5)
    assert field.to_string() == u'5'
    assert field.validate() == 5


def test_render_color():
    field = f.Color()
    field.name = u'abc'
    field.load_data('#ffaf2e')

    assert field() == field.as_input()
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


def test_render_color_extra():
    field = f.Color(data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = u'abc'
    field.load_data('#ffaf2e')

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="color" value="#ffaf2e" data-modal>')
    assert (field(foo='bar', type='text') ==
            u'<input aria-label="test" foo="bar" name="abc" type="text" value="#ffaf2e" data-modal>')


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


def test_color_default():
    field = f.Color(default='#ffaf2e')
    assert field.to_string() == u'#ffaf2e'
    assert field.validate() == u'#ffaf2e'


def test_render_boolean():
    field = f.Boolean()
    field.name = u'abc'

    field.load_data(obj_value=True)
    assert field() == field.as_checkbox()
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


def test_render_boolean_extra():
    field = f.Boolean(data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = u'abc'

    field.load_data(obj_value=True)
    assert field() == field.as_checkbox()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="checkbox" checked data-modal>')


def test_validate_boolean():
    field = f.Boolean()

    for val in [None, u'', u'0', u'no', u'off', u'false', u'NO', 'fAlsE']:
        print(val)
        field.load_data(val)
        assert field.validate() == False

    for val in [u'1', u'ok', u'yes', u'Of course!!!1', u'whatever']:
        field.load_data(val)
        assert field.validate() == True

    field = f.Boolean(validate=[f.Required])
    assert field.validate() is None
    assert field.error


def test_render_file():
    field = f.File('.')
    field.name = u'abc'

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="file">')

    field = f.File(validate=[f.Required])
    field.name = u'abc'
    assert (field() ==
            u'<input name="abc" type="file" required>')
    assert (field(required=False) ==
            u'<input name="abc" type="file">')


def test_render_file_extra():
    field = f.File(
        '.', data_modal=True, aria_label='test', foo='niet', clean=_clean,
        upload_to='aaaa', secret=False
    )
    field.name = u'abc'

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="file" data-modal>')


def test_validate_file():
    field = f.File()
    field.name = u'abc'

    field.load_data(obj_value=u'obj value')
    assert field.validate() == u'obj value'
    assert not field.error

    field.load_data(obj_value=u'obj value', file_data=u'file data')
    assert field.validate() == u'file data'
    assert not field.error


def test_field_as_dict():
    message = u'Lorem ipsum'
    field = f.Field(validate=[f.Required(message)])
    field.name = u'abc'
    assert field.validate() is None

    expdict = {
        'name': u'abc',
        'value': u'',
        'error': message,
    }
    result = sorted(list(field.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
