# coding=utf-8
import pytest
import solution as f


def test_required():
    validator = f.Required()
    assert validator(u'abc')
    assert validator(True)
    assert not validator(u'')
    assert not validator(u'  ')
    assert not validator()


def test_required_message():
    validator = f.Required(message=u'abc')
    assert validator.message == u'abc'


def test_isnumber():
    validator = f.IsNumber()
    assert validator(33)
    assert validator(2.4)
    assert validator(-4e10)
    assert not validator(u'as2')


def test_isnumber_message():
    validator = f.IsNumber(message=u'abc')
    assert validator.message == u'abc'


def test_longerthan():
    validator = f.LongerThan(4)
    assert validator(u'12345')
    assert not validator(u'123')
    assert validator(12345)
    assert not validator(12)
    assert not validator(None)


def test_longerthan_message():
    validator = f.LongerThan(4, message=u'abc')
    assert validator.message == u'abc'


def test_shorterthan():
    validator = f.ShorterThan(4)
    assert validator(u'123')
    assert not validator(u'12345')
    assert validator(123)
    assert not validator(12345)
    assert not validator(None)


def test_shorterthan_message():
    validator = f.ShorterThan(4, message=u'abc')
    assert validator.message == u'abc'


def test_lessthan():
    validator = f.LessThan(4)
    assert validator(3)
    assert not validator(5)
    assert validator(u'3')
    assert not validator(u'5')
    assert not validator(None)

    validator = f.LessThan(u'b')
    assert validator(u'a')
    assert not validator(u'c')
    assert not validator(None)


def test_lessthan_message():
    validator = f.LessThan(4, message=u'abc')
    assert validator.message == u'abc'


def test_morethan():
    validator = f.MoreThan(4)
    assert validator(5)
    assert not validator(3)
    assert not validator(u'3')
    assert validator(u'5')
    assert not validator(None)

    validator = f.MoreThan(u'b')
    assert not validator(u'a')
    assert validator(u'c')
    assert not validator(None)


def test_morethan_message():
    validator = f.MoreThan(4, message=u'abc')
    assert validator.message == u'abc'


def test_inrange():
    validator = f.InRange(4, 10)
    assert validator(4)
    assert validator(10)
    assert not validator(3)
    assert not validator(11)
    assert not validator(None)

    validator = f.InRange(u'j', u'p')
    assert not validator(u'a')
    assert validator(u'm')
    assert not validator(None)


def test_inrange_message():
    validator = f.InRange(1, 2, message=u'abc')
    assert validator.message == u'abc'


def test_match():
    validator = f.Match(r'\+\d{2}-\d')
    assert validator(u'+51-1')
    assert not validator(u'33')
    assert not validator(None)


def test_match_message():
    validator = f.Match('', message=u'abc')
    assert validator.message == u'abc'


def test_validemail():
    validator = f.ValidEmail()
    assert validator(u'juanpablo@lucumalabs.com')
    assert validator(u'juan+pablo@example.com')
    assert validator(u'jps@nic.pe')
    assert not validator(u'lalala')
    assert not validator(u'aa@a')
    assert not validator(u'fail@test,com')
    assert not validator(u'Whatever <lucumalabs.com>')
    assert not validator(None)
    assert not validator(u'.fail@test.com')


def test_validemail_wrapped():
    validator = f.ValidEmail()
    assert validator(u'"Juan Pablo Scaletti" <juanpablo@lucumalabs.com>')
    assert validator(u'"" <juanpablo@lucumalabs.com>')
    assert validator(u'<juanpablo@lucumalabs.com>')
    assert validator(u'Juan Pablo Scaletti <juanpablo@lucumalabs.com>')


def test_validemail_idna():
    validator = f.ValidEmail()
    assert validator(u'"Test" <test@mañana.com>')
    assert validator(u'<test@mañana.com>')
    assert not validator('fail@olé')


def test_validemail_message():
    validator = f.ValidEmail(message=u'abc')
    assert validator.message == u'abc'


def test_isurl():
    validator = f.ValidURL()
    assert validator(u'http://example.com')
    assert validator(u'www.archive.org')
    assert not validator('http://')
    assert not validator(u'lalala')
    assert not validator(None)


def test_isurl_idna():
    validator = f.ValidURL()
    assert validator(u'http://españa.es')
    assert validator(u'http://olé.com')
    assert validator('http://希望.org')


def test_isurl_message():
    validator = f.ValidURL(message=u'abc')
    assert validator.message == u'abc'


def test_iscolor():
    validator = f.IsColor()
    assert validator(u'#ffaf2e')
    assert not validator(u'33')
    assert not validator(None)


def test_iscolor_message():
    validator = f.IsColor(message=u'abc')
    assert validator.message == u'abc'

