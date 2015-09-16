# coding=utf-8
import datetime

import solution as f


to_unicode = f._compat.to_unicode


def _clean(form, value, **kwargs):
    return value


def test_render_time():
    field = f.Time()
    field.name = u'abc'
    field.load_data(obj_value=datetime.time(11, 55))

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="time" value="11:55 AM">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">11:55 AM</textarea>')
    assert (field(foo='bar', type='text') ==
            u'<input foo="bar" name="abc" type="text" value="11:55 AM">')


def test_render_time_extra():
    field = f.Time(data_modal=True, aria_label='test', foo='niet', clean=_clean)
    field.name = u'abc'
    field.load_data(obj_value=datetime.time(11, 55))

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="time" value="11:55 AM" data-modal>')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea aria-label="test" foo="bar" name="abc" data-modal>11:55 AM</textarea>')
    assert (field(foo='bar', type='text') ==
            u'<input aria-label="test" foo="bar" name="abc" type="text" value="11:55 AM" data-modal>')


def test_render_required():
    field = f.Time(validate=[f.Required])
    field.name = u'abc'
    assert field() == u'<input name="abc" type="time" value="" required>'
    assert field.as_textarea() == u'<textarea name="abc" required></textarea>'


def test_render_default():
    field = f.Time(default=datetime.time(9, 16))
    field.name = u'abc'
    assert field() == u'<input name="abc" type="time" value="9:16 AM">'

    field = f.Time(default=datetime.time(21, 16))
    field.name = u'abc'
    assert field() == u'<input name="abc" type="time" value="9:16 PM">'


def test_validate_time():
    field = f.Time()
    assert field.validate() is None

    field = f.Time()
    field.load_data(u'4:55 PM')
    assert field.validate() == datetime.time(16, 55)

    field = f.Time()
    field.load_data(u'4:55:13 AM')
    assert field.validate() == datetime.time(4, 55, 13)

    field = f.Time()
    field.load_data(u'invalid')
    assert field.validate() is None

    field = f.Time()
    field.load_data(u'16:23 PM')
    assert field.validate() is None


def test_validate_24hours():
    field = f.Time()
    field.load_data(u'16:23')
    assert field.validate() == datetime.time(16, 23)
    field = f.Time()
    field.load_data(u'4:23')
    assert field.validate() == datetime.time(4, 23)

    field = f.Time()
    field.load_data(u'16:23:55')
    assert field.validate() == datetime.time(16, 23, 55)


def test_validate_time_with_default():
    dt = datetime.time(4, 48, 16)
    field = f.Time(default=dt)
    assert field.validate() == dt
