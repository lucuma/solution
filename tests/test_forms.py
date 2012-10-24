# -*- coding: utf-8 -*-
import pytest

from solution import forms as f
from solution import SQLAlchemy


class ContactForm(f.Form):
    subject = f.Text(validate=[f.Required])
    email = f.Email()
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
        'email': '<input name="email" type="email" value="">',
        'message': '<input name="message" type="text" value="" required>',
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
        'subject': '<input name="subject" type="text" value="%s" required>' % data['subject'],
        'email': '<input name="email" type="email" value="">',
        'message': '<input name="message" type="text" value="%s" required>' % data['message'],
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
        'subject': '<input name="subject" type="text" value="%s" required>' % data['subject'],
        'email': '<input name="email" type="email" value="%s">' % obj['email'],
        'message': '<input name="message" type="text" value="%s" required>' % data['message'],
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
    print obj.keys()
    assert obj['subject'] == data['subject']
    assert obj['message'] == data['message']


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
        'email': u''
    }
    form.subject.value = data['subject']
    form.message.value = data['message']
    assert form.is_valid()
    assert form.changed_fields == ['message', 'subject']
    assert form.cleaned_data['subject'] == data['subject']
    assert form.cleaned_data['message'] == data['message']
    assert form.cleaned_data['email'] == None


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
    expected = '<input name="meh-email" type="email" value="%s">' % obj['email']
    assert str(form.email) == expected

    assert form.is_valid()
    obj = form.save()
    print obj.keys()
    assert obj['subject'] == data['meh-subject']
    assert obj['message'] == data['meh-message']


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
        email = f.Email()
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
    print 'contact', contact.to_dict()
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
        email = f.Email()
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
        'a1': u'AAA1',
        'a2': u'AAA2',
        'b1': u'BBB1',
        'b2': u'BBB2',
    }
    form = WrapForm(data)

    assert form.is_valid()
    form.save()
    db.commit()
    assert db.query(ModelA).count() == 1
    assert db.query(ModelB).count() == 1
    obja = db.query(ModelA).first()
    assert obja.a1 == data['a1']
    assert obja.a2 == data['a2']
    objb = db.query(ModelB).first()
    assert objb.b1 == data['b1']
    assert objb.b2 == data['b2']

    ## Update
    data = {
        'wr': u'foo',
        'a1': u'A1',
        'a2': u'A2',
        'b1': u'B1',
        'b2': u'B2',
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
    assert obja.a1 == data['a1']
    assert obja.a2 == data['a2']

    objb = db.query(ModelB).first()
    assert objb.b1 == data['b1']
    assert objb.b2 == data['b2']



def test_formset_as_field():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    class WrapForm(f.Form):
        s = f.FormSet(MyForm)

    obj = {
        's': [
            {'a': 'A1', 'b': 'B1'},
            {'a': 'A2', 'b': 'B2'},
        ],
    }
    form = WrapForm(obj=obj)
    assert form.is_valid()
    for sf in form.s:
        assert sf.cleaned_data


def test_formset_objs():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    objs=[
        {'a': 'A1', 'b': 'B1'},
        {'a': 'A2', 'b': 'B2'},
        {'a': 'A3', 'b': 'B3'},
        {'a': 'A4', 'b': 'B4'},
    ]
    fset = f.FormSet(MyForm, data={}, objs=objs)
    assert len(fset._forms) == 4
    for i, form in enumerate(fset):
        expected = '<input name="myform.%i-a" type="text" value="%s" required>' % (i+1, objs[i]['a'])
        assert str(form.a) == expected
        assert form.is_valid()
    assert fset.is_valid()


def test_formset_new_forms():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    data={
        'myform.1-a': 'a first',
        'myform.1-b': 'b first',
        'myform.2-a': 'a second',
        'myform.2-b': 'b second',
    }
    fset = f.FormSet(MyForm, data=data)
    assert len(fset._forms) == 2
    for form in fset:
        assert form.is_valid()
    assert fset.is_valid()


def test_formset_model():
    db = SQLAlchemy()

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)

    class Address(db.Model):
        __tablename__ = 'addresses'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        user = db.relationship('User',
            backref=db.backref('addresses', lazy='dynamic'))

        def __repr__(self):
            return '<Address %s>' % (self.email,)

    db.create_all()

    class FormAddress(f.Form):
        _model = Address
        email = f.Email()

        def __repr__(self):
            return '<FormAddress %s>' % (self.email.value,)

    class FormUser(f.Form):
        _model = User
        name = f.Text()
        addresses = f.FormSet(FormAddress, parent='user')

    ## Save

    data = {
        'name': u'John Doe',
        'formaddress.1-email': u'one@example.com',
        'formaddress.2-email': u'two@example.com',
        'formaddress.3-email': u'three@example.com',
    }
    form = FormUser(data)
    assert form.is_valid()
    user = form.save()
    db.commit()

    assert db.query(User).count() == 1
    assert db.query(Address).count() == 3
    addr = db.query(Address).first()
    assert addr.email == data['formaddress.1-email']
    assert addr.user == user

    ## Update

    user = db.query(User).first()
    data = {
        'name': u'Max Smart',
        'formaddress.1-email': u'one+1@example.com',
        'formaddress.2-email': u'two+2@example.com',
        'formaddress.3-email': u'three+3@example.com',
    }
    form = FormUser(data, obj=user)
    assert form.is_valid()
    form.save()
    db.commit()

    assert user.name == data['name']
    assert db.query(Address).count() == 3
    addr = db.query(Address).first()
    assert addr.email == data['formaddress.1-email']
    assert addr.user == user


def test_formset_missing_objs():
    db = SQLAlchemy()

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)

    class Address(db.Model):
        __tablename__ = 'addresses'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        user = db.relationship('User',
            backref=db.backref('addresses', lazy='dynamic'))

        def __repr__(self):
            return self.email

    db.create_all()

    class FormAddress(f.Form):
        _model = Address
        id = f.Integer()
        email = f.Email()

        def __repr__(self):
            return '<FormAddress %s>' % (self.email.value,)

    class FormUser(f.Form):
        _model = User
        id = f.Integer()
        name = f.Text()
        addresses = f.FormSet(FormAddress, parent='user')

    user = User(name=u'John Doe')
    db.add(user)
    a1 = Address(id=1, email=u'one@example.com', user=user)
    db.add(a1)
    a2 = Address(id=2, email=u'two@example.com', user=user)
    db.add(a2)
    a3 = Address(id=3, email=u'three@example.com', user=user)
    db.add(a3)
    db.commit()

    data = {
        'name': u'Jane Doe',
        'formaddress.1-email': u'one@example.org',
        'formaddress.3-email': u'three@example.org',
        'formaddress.4-email': u'four@example.org',
    }
    print [(a.id, a.email) for a in user.addresses]
    form = FormUser(data, user)
    assert form.is_valid()
    assert form.addresses.missing_objs == [a2]

