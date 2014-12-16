# coding=utf-8
import datetime

import pytest
import solution as f


def test_isdate():
    validator = f.IsDate()
    assert validator(datetime.date.today())
    assert validator(datetime.datetime.utcnow())
    assert not validator(None)
    assert not validator(u'2012-04-13')


def test_before():
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = f.Before(now)
    assert validator(now - delta)
    assert not validator(now + delta)
    assert not validator(None)

    now = datetime.date.today()
    delta = datetime.timedelta(days=1)
    validator = f.Before(now)
    assert validator(now - delta)
    assert not validator(now + delta)


def test_before_message():
    now = datetime.datetime.utcnow()
    validator = f.Before(now, message=u'abc')
    assert validator.message == u'abc'


def test_after():
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = f.After(now)
    assert validator(now + delta)
    assert not validator(now - delta)
    assert not validator(None)

    now = datetime.date.today()
    delta = datetime.timedelta(days=1)
    validator = f.After(now)
    assert validator(now + delta)
    assert not validator(now - delta)


def test_after_message():
    now = datetime.datetime.utcnow()
    validator = f.After(now, message=u'abc')
    assert validator.message == u'abc'


def test_beforenow():
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = f.BeforeNow()
    assert validator(now - delta)
    assert not validator(now + delta)
    assert not validator(None)


def test_beforenow_message():
    validator = f.BeforeNow(message=u'abc')
    assert validator.message == u'abc'


def test_afternow():
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=1)
    validator = f.AfterNow()
    assert validator(now + delta)
    assert not validator(now - delta)
    assert not validator(None)


def test_afternow_message():
    validator = f.AfterNow(message=u'abc')
    assert validator.message == u'abc'


def test_isdate_message():
    validator = f.IsDate(message=u'abc')
    assert validator.message == u'abc'


def test_validsplitdate():
    data = {
        'month': u'3',
        'day': u'30',
        'year': u'2013'
    }
    validator = f.ValidSplitDate('day', 'month', 'year', message='fail!')
    assert validator(data)
    assert validator.message == 'fail!'

    data = {
        'month': u'3',
        'day': u'30',
    }
    validator = f.ValidSplitDate('day', 'month')
    assert validator(data)

    data = {
        'month': u'2',
        'day': u'30',
    }
    validator = f.ValidSplitDate('day', 'month')
    assert not validator(data)
