# -*- coding: utf-8 -*-
import datetime

import pytest
import solution as f


def test_areequal():
    data = {
        'password': u'lalala',
        're_password': u'lalala',
    }
    validator = f.AreEqual('password', 're_password', plural='passwords')
    assert validator(data)

    data['re_password'] = u''
    assert not validator(data)
    assert validator.message ==  u'The passwords doesn\'t match.'


def test_atleastone():
    data = {
        'a': u'lalala',
        'b': u'lalala',
    }
    validator = f.AtLeastOne(['z', 'b', 'x'], message='fail!')
    assert validator(data)
    assert validator.message == 'fail!'

    validator = f.AtLeastOne(['a', 'b'])
    assert validator(data)

    validator = f.AtLeastOne(['z', 'x'])
    assert not validator(data)


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

