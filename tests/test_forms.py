# -*- coding: utf-8 -*-
import pytest

from solution.forms import Form
from solution.forms import fields as f
from solution.forms import validators as v


class ContactForm(Form):
    subject = f.Text(v.Required)
    email = f.Email()
    message = f.Text(
        v.Required(message=u'write something!')
    )


def test_declaration():
    form = ContactForm()
    assert not form.has_changed


def test_fields():
    form = ContactForm()
    expected = {
        'message': '<input name="message" type="text" value="">',
        'email': '<input name="email" type="email" value="">',
        'subject': '<input name="subject" type="text" value="">',
    }
    for field in form:
        assert expected[field.name] == str(field)


def test_initial_data():
    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    form = ContactForm(data)
    expected = {
        'message': '<input name="message" type="text" value="%s">' % data['message'],
        'email': '<input name="email" type="email" value="">',
        'subject': '<input name="subject" type="text" value="%s">' % data['subject'],
    }
    for field in form:
        assert expected[field.name] == str(field)


def test_obj_data():
    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    obj = {
        'email': u'info@lucumalabs.com',
    }
    form = ContactForm(data, obj=obj)
    expected = {
        'message': '<input name="message" type="text" value="%s">' % data['message'],
        'email': '<input name="email" type="email" value="%s">' % obj['email'],
        'subject': '<input name="subject" type="text" value="%s">' % data['subject'],
    }
    for field in form:
        assert expected[field.name] == str(field)


def test_is_valid():
    form = ContactForm()
    assert not form.is_valid()
    assert form._errors

    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    form = ContactForm(data)
    print form._errors
    assert form.is_valid()
    assert not form._errors  


def test_has_changed():
    form = ContactForm()
    assert not form.is_valid()
    assert not form.has_changed

    data = {
        'subject': u'Lalala',
        'message': u'Lalala',
    }
    form.subject.value = data['subject']
    form.message.value = data['message']
    assert form.is_valid()
    assert form.has_changed


def test_changed_data():
    form = ContactForm()
    data = {
        'subject': u'Lalala',
        'message': u'Lalala',
        'email': None
    }
    form.subject.value = data['subject']
    form.message.value = data['message']
    assert form.is_valid()
    assert form.changed_fields == ['message', 'subject']
    assert form.cleaned_data == data

