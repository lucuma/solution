# coding=utf-8
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
    validator = f.AtLeastOne(['z', 'b', 'x'])
    assert validator(data)

    validator = f.AtLeastOne(['a', 'b'])
    assert validator(data)

    validator = f.AtLeastOne(['z', 'x'])
    assert not validator(data)

