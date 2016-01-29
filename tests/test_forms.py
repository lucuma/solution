# coding=utf-8
from __future__ import print_function

from sqlalchemy_wrapper import SQLAlchemy
import solution as f


class ContactForm(f.Form):
    subject = f.Text(validate=[f.Required(u'required')])
    email = f.Text(validate=[f.ValidEmail])
    message = f.Text(validate=[
        f.Required(message=u'write something!')
    ])


def test_declaration():
    form = ContactForm()
    assert not form.has_changed


def test_fields():
    form = ContactForm()
    expected = {
        'subject': '<input name="subject" type="text" value="" required>',
        'email': '<input name="email" type="text" value="">',
        'message': '<input name="message" type="text" value="" required>',
    }
    for field in form:
        assert expected[field.name] == field()


def test_initial_data():
    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    form = ContactForm(data)
    expected = {
        'subject': '<input name="subject" type="text" value="%s" required>' % data['subject'],
        'email': '<input name="email" type="text" value="">',
        'message': '<input name="message" type="text" value="%s" required>' % data['message'],
    }
    for field in form:
        assert expected[field.name] == field()


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
        'subject': '<input name="subject" type="text" value="{}" required>'.format(
            data['subject']
        ),
        'email': '<input name="email" type="text" value="{}">'.format(
            obj['email']
        ),
        'message': '<input name="message" type="text" value="{}" required>'.format(
            data['message']
        ),
    }
    for field in form:
        assert expected[field.name] == field()


def test_is_valid():
    form = ContactForm()
    assert not form.is_valid()
    assert form._errors

    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    form = ContactForm(data)
    print(form._errors)
    assert form.is_valid()
    assert not form._errors


def test_empty_data():

    class MyForm(f.Form):
        meh = f.Text()

    data = {
        'meh': u'',
    }
    obj = {
        'meh': u'lalala',
    }
    form = MyForm(data, obj=obj)
    assert form.is_valid()
    assert form.cleaned_data['meh'] == u''


def test_dict_save():
    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    form = ContactForm(data)
    obj = form.save()
    print(obj.keys())
    assert obj['subject'] == data['subject']
    assert obj['message'] == data['message']


def test_manipulate_cleaned_data_and_save():
    data = {
        'subject': u'Hello',
        'message': u'Welcome',
    }
    form = ContactForm(data)
    assert form.is_valid()
    form.cleaned_data.pop('message')
    obj = form.save()
    assert list(obj.keys()) == ['subject']
    assert obj['subject'] == data['subject']


def test_has_changed():
    form = ContactForm()
    assert not form.is_valid()
    assert not form.has_changed

    data = {
        'subject': u'Lalala',
        'message': u'Lalala',
    }
    form = ContactForm(data)
    assert form.is_valid()
    assert form.has_changed
    assert sorted(form.changed_fields) == sorted(['message', 'subject'])


def test_prefix():
    data = {
        'meh-subject': u'Hello',
        'meh-message': u'Welcome',
    }
    obj = {
        'email': u'foo@bar.com',
    }
    form = ContactForm(data, obj=obj, prefix='meh')
    expected = '<input name="meh-subject" type="text" value="%s" required>' % data['meh-subject']
    assert str(form.subject) == expected
    expected = '<input name="meh-email" type="text" value="%s">' % obj['email']
    assert str(form.email) == expected

    assert form.is_valid()
    obj = form.save()
    print(obj.keys())
    assert obj['subject'] == data['meh-subject']
    assert obj['message'] == data['meh-message']


def test_clean_fields():

    class MyContactForm(f.Form):
        subject = f.Text()
        email = f.Text()
        message = f.Text()

        def clean_subject(self, py_value, **kwargs):
            return 'foobar ' + py_value

        def clean_email(self, py_value, **kwargs):
            return 'foobar ' + py_value

    form = MyContactForm({
        'subject': u'abc',
        'email': u'abc',
        'message': u'abc',
    })
    assert form.is_valid()
    assert form.cleaned_data['subject'] == 'foobar abc'
    assert form.cleaned_data['email'] == 'foobar abc'


def test_clean_fields_error():

    class MyContactForm(f.Form):
        subject = f.Text(validate=[f.Required])
        email = f.Text(validate=[f.Required])
        message = f.Text(validate=[f.Required])

        def clean_subject(self, py_value, **kwargs):
            raise f.ValidationError

    form = MyContactForm({
        'subject': u'abc',
        'email': u'abc',
        'message': u'abc',
    })
    assert not form.is_valid()


def test_save():
    db = SQLAlchemy()

    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        subject = db.Column(db.Unicode, nullable=False)
        email = db.Column(db.Unicode)
        message = db.Column(db.UnicodeText, nullable=False)

    db.create_all()

    class MyContactForm(f.Form):
        _model = Contact

        subject = f.Text(validate=[f.Required])
        email = f.Text(validate=[f.ValidEmail])
        message = f.Text(validate=[
            f.Required(message=u'write something!')
        ])

    # Create new object
    data = {
        'subject': u'foo',
        'message': u'bar',
        'email': u'test@example.com',
    }
    form = MyContactForm(data)
    assert form.is_valid()
    contact = form.save()
    print('contact', contact.__dict__)
    assert isinstance(contact, Contact)
    assert contact.id is None
    assert contact.subject == data['subject']
    assert contact.message == data['message']
    assert contact.email == data['email']
    db.commit()

    # Update object
    data['message'] = u'lalala'
    form = MyContactForm(data, obj=contact)
    assert form.is_valid()
    contact = form.save()
    assert contact.id is not None
    assert contact.message == data['message']
    db.commit()


def init_subform_with_instances():
    class FormA(f.Form):
        a = f.Text()

    class WrapForm(f.Form):
        fa = FormA()

    data = {
        'fa.a': u'A',
    }
    form = WrapForm(data)
    assert form.save() == data

    user_data = {
        'fa.a': u'AAA',
    }
    form = WrapForm(user_data, data)
    assert form.save() == user_data


def init_subform_with_classes():
    class FormA(f.Form):
        a = f.Text()

    class WrapForm(f.Form):
        fa = FormA

    data = {
        'fa.a': u'A',
    }
    form = WrapForm(data)
    assert form.save() == data

    user_data = {
        'fa.a': u'AAA',
    }
    form = WrapForm(user_data, data)
    assert form.save() == user_data


def test_prefix_save():
    db = SQLAlchemy()

    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        subject = db.Column(db.Unicode, nullable=False)
        email = db.Column(db.Unicode)
        message = db.Column(db.UnicodeText, nullable=False)

    db.create_all()

    class MyContactForm(f.Form):
        _model = Contact

        subject = f.Text(validate=[f.Required])
        email = f.Text(validate=[f.ValidEmail])
        message = f.Text(validate=[
            f.Required(message=u'write something!')
        ])

    data = {
        'meh-subject': u'Hello',
        'meh-message': u'Welcome',
    }
    form = MyContactForm(data, prefix='meh')
    assert form.is_valid()
    contact = form.save()
    assert isinstance(contact, Contact)
    db.commit()
    assert contact.subject == data['meh-subject']
    assert contact.message == data['meh-message']

    data = {
        'meh-subject': u'foo',
        'meh-message': u'bar',
    }
    form = MyContactForm(data, obj=contact, prefix='meh')
    assert form.is_valid()
    assert form.has_changed
    form.save()
    db.commit()
    assert contact.subject == data['meh-subject']
    assert contact.message == data['meh-message']


def test_cascade_save():
    db = SQLAlchemy()

    class ModelA(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        a1 = db.Column(db.Unicode, nullable=False)
        a2 = db.Column(db.Unicode)

    class ModelB(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        b1 = db.Column(db.Unicode, nullable=False)
        b2 = db.Column(db.Unicode)

    db.create_all()

    class FormA(f.Form):
        _model = ModelA

        a1 = f.Text(validate=[f.Required])
        a2 = f.Text()

    class FormB(f.Form):
        _model = ModelB

        b1 = f.Text(validate=[f.Required])
        b2 = f.Text()

    class WrapForm(f.Form):
        wr = f.Text()
        fa = FormA()
        fb = FormB()

    data = {
        'wr': u'foo',
        'fa.a1': u'AAA1',
        'fa.a2': u'AAA2',
        'fb.b1': u'BBB1',
        'fb.b2': u'BBB2',
    }
    form = WrapForm(data)

    assert form.is_valid()
    form.save()
    db.commit()
    assert db.query(ModelA).count() == 1
    assert db.query(ModelB).count() == 1
    obja = db.query(ModelA).first()
    assert obja.a1 == data['fa.a1']
    assert obja.a2 == data['fa.a2']
    objb = db.query(ModelB).first()
    assert objb.b1 == data['fb.b1']
    assert objb.b2 == data['fb.b2']

    # Update
    data = {
        'wr': u'foo',
        'fa.a1': u'A1',
        'fa.a2': u'A2',
        'fb.b1': u'B1',
        'fb.b2': u'B2',
    }
    objs = {
        'fa': obja,
        'fb': objb
    }
    form = WrapForm(data, obj=objs)
    assert form.is_valid()
    form.save()
    db.commit()

    assert db.query(ModelA).count() == 1
    assert db.query(ModelB).count() == 1

    obja = db.query(ModelA).first()
    assert obja.a1 == data['fa.a1']
    assert obja.a2 == data['fa.a2']

    objb = db.query(ModelB).first()
    assert objb.b1 == data['fb.b1']
    assert objb.b2 == data['fb.b2']


def test_form_data_prepare_and_clean():

    class ContactForm(f.Form):
        subject = f.Text(validate=[f.Required])
        message = f.Text(validate=[f.Required])

        def prepare(self, data):
            data['message'] = u'Welcome'
            data['subject'] = data['greeting'] + u' World'
            return data

        def clean(self, cleaned_data):
            #: Any field that isn't in the form is filtered out
            return {
                'message': u'{subject}. {message}'.format(**cleaned_data),
                'loremipsum': u'I am filtered out',
            }

    data = {
        'greeting': u'Hello',
    }
    form = ContactForm(data)

    assert form.subject.value == u'Hello World'
    assert form.message.value == u'Welcome'

    cleaned_data = form.save()
    assert cleaned_data == {'message': u'Hello World. Welcome'}


def test_missing_fields_obj():
    db = SQLAlchemy()

    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        subject = db.Column(db.Unicode)

    db.create_all()

    class ContactForm(f.Form):
        _model = Contact
        subject = f.Text()

    contact = Contact(subject=u'foobar')
    db.add(contact)
    db.commit()

    form = ContactForm({}, contact)
    new_contact = form.save()
    assert new_contact.subject == u'foobar'

    form = ContactForm({'subject': u''}, contact)
    new_contact = form.save()
    assert new_contact.subject == u''


def test_missing_fields_dict():

    class ContactForm(f.Form):
        subject = f.Text()

    contact = {
        'subject': u'foobar',
    }
    form = ContactForm({}, contact)
    new_contact = form.save()
    assert new_contact['subject'] == u'foobar'

    form = ContactForm({'subject': u''}, contact)
    new_contact = form.save()
    assert new_contact['subject'] == u''


def test_delete_field():
    data = {
        'subject': u'Hello',
        'message': u'Welcome',
        'email': u'elliot.anderson@ecorp.com',
        'email__deleted': 1,
    }
    form = ContactForm(data)
    obj = form.save()
    print(obj.keys())
    assert obj['email'] == None
    assert obj['subject'] == data['subject']
    assert obj['message'] == data['message']


def test_delete_file_field():
    class ProfileForm(f.Form):
        photo = f.File()

    profile = {
        'photo': u'a/b/c.png',
    }
    data = {
        'photo': u'',
        'photo__deleted': 1,
    }
    form = ProfileForm(data, profile)
    obj = form.save()
    assert obj['photo'] == None


def test_simple_form_as_dict():
    data = {
        'subject': u'Hello',
    }
    obj = {
        'email': u'info@lucumalabs.com',
    }
    form = ContactForm(data, obj=obj)

    expdict = {
        u'subject': {
            'name': u'subject',
            'value': data[u'subject'],
            'error': u'',
        },
        u'email': {
            'name': u'email',
            'value': obj['email'],
            'error': u'',
        },
        u'message': {
            'name': u'message',
            'value': u'',
            'error': u'',
        },
    }
    result = sorted(list(form.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected

    assert not form.is_valid()
    expdict = {
        u'subject': {
            'name': u'subject',
            'value': data[u'subject'],
            'error': u'',
        },
        u'email': {
            'name': u'email',
            'value': obj['email'],
            'error': u'',
        },
        u'message': {
            'name': u'message',
            'value': u'',
            'error': u'write something!',
        },
    }
    result = sorted(list(form.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
    assert form.as_json()


def test_simple_prefixed_form_as_dict():
    data = {
        'meh-subject': u'Hello',
    }
    obj = {
        'email': u'info@lucumalabs.com',
    }
    form = ContactForm(data, obj=obj, prefix=u'meh')

    expdict = {
        u'meh-subject': {
            'name': u'meh-subject',
            'value': data[u'meh-subject'],
            'error': u'',
        },
        u'meh-email': {
            'name': u'meh-email',
            'value': obj['email'],
            'error': u'',
        },
        u'meh-message': {
            'name': u'meh-message',
            'value': u'',
            'error': u'',
        },
    }
    print(form.as_dict())
    result = sorted(list(form.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
    assert form.as_json()


def test_form_with_subform_as_dict():
    class FormA(f.Form):
        a = f.Text()

    class WrapForm(f.Form):
        fa = FormA

    data = {
        'fa.a': u'A',
    }
    form = WrapForm(data)

    expdict = {
        'fa': {
            'fa.a': {
                'name': u'fa.a',
                'value': u'A',
                'error': u'',
            }
        },
    }
    result = sorted(list(form.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
    assert form.as_json()


def test_form_with_formset_as_dict():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    class WrapForm(f.Form):
        subs = f.FormSet(MyForm)

    form = WrapForm({'subs.1-a': 'foo', 'subs.2-b': 'bar'})

    expdict = {
        'subs': [
            {
                'subs.1-a': {
                    'name': u'subs.1-a',
                    'value': u'foo',
                    'error': u'',
                },
                'subs.1-b': {
                    'name': u'subs.1-b',
                    'value': u'',
                    'error': u'',
                },
            },
            {
                'subs.2-a': {
                    'name': u'subs.2-a',
                    'value': u'',
                    'error': u'',
                },
                'subs.2-b': {
                    'name': u'subs.2-b',
                    'value': u'bar',
                    'error': u'',
                },
            },
        ],

        '_subs_form': {
            'subs.1-a': {
                'name': u'subs.1-a',
                'value': u'',
                'error': u'',
            },
            'subs.1-b': {
                'name': u'subs.1-b',
                'value': u'',
                'error': u'',
            },
        },
    }
    print(form.as_dict())
    result = sorted(list(form.as_dict().items()))
    expected = sorted(list(expdict.items()))
    assert result == expected
    assert form.as_json()
