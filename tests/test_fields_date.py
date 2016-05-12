# coding=utf-8
from datetime import datetime

import pytz
import solution as f


to_unicode = f._compat.to_unicode


def _clean(form, value, **kwargs):
    return value


def test_render_date():
    field = f.Date(tz='America/Lima')  # utc-5
    field.name = u'abc'
    field.load_data(obj_value=datetime(1979, 5, 30, 4, 0, 0))

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="date" value="1979-05-29">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">1979-05-29</textarea>')
    assert (field(foo='bar', type='text') ==
            u'<input foo="bar" name="abc" type="text" value="1979-05-29">')


def test_render_date_extra():
    field = f.Date(tz='America/Lima', data_modal=True, aria_label='test',
                   foo='niet', clean=_clean)
    field.name = u'abc'
    field.load_data(obj_value=datetime(1979, 5, 30, 4, 0, 0))

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input aria-label="test" foo="bar" name="abc" type="date" value="1979-05-29" data-modal>')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea aria-label="test" foo="bar" name="abc" data-modal>1979-05-29</textarea>')
    assert (field(foo='bar', type='text') ==
            u'<input aria-label="test" foo="bar" name="abc" type="text" value="1979-05-29" data-modal>')


def test_render_required():
    field = f.Date(validate=[f.Required])
    field.name = u'abc'
    assert field() == u'<input name="abc" type="date" value="" required>'
    assert field.as_textarea() == u'<textarea name="abc" required></textarea>'


def test_render_default():
    field = f.Date(default=datetime(2013, 7, 28, 4, 0, 0))  # default tz is utc
    field.name = u'abc'
    assert field() == u'<input name="abc" type="date" value="2013-07-28">'

    field = f.Date(tz='America/Lima', default=datetime(2013, 7, 28, 4, 0, 0))
    field.name = u'abc'
    assert field() == u'<input name="abc" type="date" value="2013-07-27">'


# def test_validate_date():
#     field = f.Date(tz='America/Lima')
#     assert field.validate() is None

#     field = f.Date(tz='America/Lima')
#     field.load_data(u'1979-05-13')
#     assert field.validate() == datetime(1979, 5, 13, 5, 0, 0, tzinfo=pytz.utc)

#     field = f.Date(tz='America/Lima')
#     field.load_data([u'1979-05-13'])
#     assert field.validate() == datetime(1979, 5, 13, 5, 0, 0, tzinfo=pytz.utc)

#     field = f.Date(tz='America/Lima')
#     field.load_data(u'invalid')
#     assert field.validate() is None


def test_validate_date_with_default():
    now = datetime.utcnow()
    field = f.Date(default=now)
    assert field.validate() == now


def test_form_tz():
    class MyForm(f.Form):
        mydate = f.Date()

    dt = datetime(1979, 5, 30, 4, 0, 0)
    form = MyForm({}, {'mydate': dt}, tz='America/Lima')
    assert form.mydate.as_input() == u'<input name="mydate" type="date" value="1979-05-29">'
