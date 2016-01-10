# coding=utf-8
from datetime import datetime

import pytz
import solution as f


to_unicode = f._compat.to_unicode


def _clean(form, value, **kwargs):
    return value


def test_render_field():
    field = f.SplittedDateTime(tz='America/Lima')  # utc-5
    field.name = u'abc'
    field.load_data(obj_value=datetime(1979, 5, 30, 4, 20, 0))

    assert field() == field.as_inputs()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="date" value="1979-05-29">'
            u'<input foo="bar" name="abc" type="time" value="11:20 PM">')
    assert (field(foo='bar', type='text') ==
            u'<input foo="bar" name="abc" type="text" value="1979-05-29">'
            u'<input foo="bar" name="abc" type="text" value="11:20 PM">')

    assert (field.as_input_date(foo='bar') ==
            u'<input foo="bar" name="abc" type="date" value="1979-05-29">')
    assert (field.as_input_time(foo='bar') ==
            u'<input foo="bar" name="abc" type="time" value="11:20 PM">')


def test_render_date_extra():
    field = f.SplittedDateTime(tz='America/Lima', data_modal=True, aria_label='test',
                               foo='niet', clean=_clean)
    field.name = u'abc'
    field.load_data(obj_value=datetime(1979, 5, 30, 4, 20, 0))

    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="date" value="1979-05-29" data-modal>'
            u'<input aria-label="test" foo="bar" name="abc" type="time" value="11:20 PM" data-modal>')


def test_render_required():
    field = f.SplittedDateTime(validate=[f.Required])
    field.name = u'abc'
    assert (field() ==
            u'<input name="abc" type="date" value="" required>'
            u'<input name="abc" type="time" value="" required>')


def test_render_default():
    field = f.SplittedDateTime(default=datetime(2013, 7, 28, 16, 20, 0))  # default tz is utc
    field.name = u'abc'
    assert (field() ==
            u'<input name="abc" type="date" value="2013-07-28">'
            u'<input name="abc" type="time" value="4:20 PM">')

    field = f.SplittedDateTime(tz='America/Lima', default=datetime(2013, 7, 28, 16, 20, 0))
    field.name = u'abc'
    assert (field() ==
            u'<input name="abc" type="date" value="2013-07-28">'
            u'<input name="abc" type="time" value="11:20 AM">')


def test_validate_date():
    field = f.SplittedDateTime(tz='America/Lima')
    assert field.validate() is None

    field = f.SplittedDateTime(tz='America/Lima')
    field.load_data([u'1979-05-13'])
    assert field.validate() == datetime(1979, 5, 13, 5, 0, 0, tzinfo=pytz.utc)

    field = f.SplittedDateTime(tz='America/Lima')
    field.load_data([u'1979-05-13', u'8:14 PM'])
    assert field.validate() == datetime(1979, 5, 14, 1, 14, 0, tzinfo=pytz.utc)

    field = f.SplittedDateTime(tz='America/Lima')
    field.load_data([u'1979-05-13', u'20:14'])
    assert field.validate() == datetime(1979, 5, 14, 1, 14, 0, tzinfo=pytz.utc)

    field = f.SplittedDateTime(tz='America/Lima')
    field.load_data([u'invalid', u'20:14'])
    assert field.validate() is None


def test_validate_date_with_default():
    now = datetime.utcnow()
    field = f.SplittedDateTime(default=now)
    assert field.validate() == now
