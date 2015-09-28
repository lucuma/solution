# coding=utf-8
from __future__ import print_function

import solution as f
from sqlalchemy_wrapper import SQLAlchemy


def test_formset_as_field():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    class WrapForm(f.Form):
        s = f.FormSet(MyForm)

    data = {
        's': [
            {'a': 'A1', 'b': 'B1'},
            {'a': 'A2', 'b': 'B2'},
        ],
    }
    form = WrapForm(data)
    assert form.is_valid()
    for sf in form.s:
        assert sf.cleaned_data


def test_formset_get_fullname():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    objs = [
        {'a': 'A1', 'b': 'B1'},
        {'a': 'A2', 'b': 'B2'},
        {'a': 'A3', 'b': 'B3'},
    ]
    formset = f.FormSet(MyForm, data={}, objs=objs)
    assert formset._forms[0]._prefix == 'myform.1-'
    assert formset._forms[1]._prefix == 'myform.2-'
    assert formset._forms[2]._prefix == 'myform.3-'

    formset = f.FormSet(MyForm, data={}, objs=objs, name='yeah')
    assert formset._forms[0]._prefix == 'yeah.1-'
    assert formset._forms[1]._prefix == 'yeah.2-'
    assert formset._forms[2]._prefix == 'yeah.3-'


def test_formset_objs():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    objs = [
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


def test_formset_new_forms():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    data = {
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
        user = db.relationship(
            'User', backref=db.backref('addresses', lazy='dynamic')
        )

        def __repr__(self):
            return '<Address %s>' % (self.email,)

    db.create_all()

    class FormAddress(f.Form):
        _model = Address
        email = f.Text(validate=[f.ValidEmail])

        def __repr__(self):
            return '<FormAddress %s>' % (self.email.value,)

    class FormUser(f.Form):
        _model = User
        name = f.Text()
        addresses = f.FormSet(FormAddress, parent='user')

    # Save

    data = {
        'name': u'John Doe',
        'addresses.1-email': u'one@example.com',
        'addresses.2-email': u'two@example.com',
        'addresses.3-email': u'three@example.com',
    }
    form = FormUser(data)
    assert form.is_valid()
    user = form.save()
    db.commit()

    assert db.query(User).count() == 1
    assert db.query(Address).count() == 3
    addr = db.query(Address).first()
    assert addr.email == data['addresses.1-email']
    assert addr.user == user

    # Update

    user = db.query(User).first()
    data = {
        'name': u'Max Smart',
        'addresses.1-email': u'one+1@example.com',
        'addresses.2-email': u'two+2@example.com',
        'addresses.3-email': u'three+3@example.com',
    }
    form = FormUser(data, obj=user)
    assert form.is_valid()
    form.save()
    db.commit()

    assert user.name == data['name']
    assert db.query(Address).count() == 3
    addr = db.query(Address).first()
    assert addr.email == data['addresses.1-email']
    assert addr.user == user


def test_formset_delete_objs():
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
        user = db.relationship(
            'User', backref=db.backref('addresses', lazy='dynamic')
        )

        def __repr__(self):
            return self.email

    db.create_all()

    class FormAddress(f.Form):
        _model = Address
        email = f.Text(validate=[f.ValidEmail])

        def __repr__(self):
            return '<FormAddress %s>' % (self.email.value,)

    class FormUser(f.Form):
        _model = User
        name = f.Text()
        addresses = f.FormSet(FormAddress, parent='user')

    user = User(name=u'John Doe')
    db.add(user)
    a1 = Address(email=u'one@example.com', user=user)
    db.add(a1)
    a2 = Address(email=u'two@example.com', user=user)
    db.add(a2)
    a3 = Address(email=u'three@example.com', user=user)
    db.add(a3)
    db.commit()
    print([(a.id, a.email) for a in user.addresses])

    data = {
        'name': u'Jane Doe',
        'addresses.1-email': u'one@example.org',
        'addresses.3-email': u'three@example.org',
        'addresses.4-email': u'four@example.org',
    }
    form = FormUser(data, user)
    assert form.is_valid()
    assert not form.addresses.missing_objs

    data = {
        'name': u'Jane Doe',
        'addresses.1-email': u'one@example.org',
        'addresses.2__deleted': u'1',
        'addresses.3-email': u'three@example.org',
        'addresses.4-email': u'four@example.org',
    }
    form = FormUser(data, user)
    assert form.is_valid()
    assert form.addresses.missing_objs == [a2]


def test_formset_save_to_dict():

    class FormAddress(f.Form):
        email = f.Text(validate=[f.ValidEmail])

    class FormUser(f.Form):
        name = f.Text()
        addresses = f.FormSet(FormAddress, parent='user')

    # Save

    data = {
        'name': u'John Doe',
        'addresses.1-email': u'one@example.com',
        'addresses.2-email': u'two@example.com',
        'addresses.3-email': u'three@example.com',
    }
    form = FormUser(data)

    assert form.save() == {
        'name': u'John Doe',
        'addresses': [
            {'email': u'one@example.com'},
            {'email': u'two@example.com'},
            {'email': u'three@example.com'},
        ],
    }


def test_save_conflicting_field_names():

    class FormValue(f.Form):
        val = f.Text()

    class FormUser(f.Form):
        name = f.Text()
        values = f.FormSet(FormValue, parent='user')

    # Save

    data = {
        'name': u'John Doe',
        'values.1-val': u'one',
        'values.2-val': u'two',
        'values.3-val': u'three',
    }
    form = FormUser(data)

    print ('-' * 30)
    result = form.save()
    print('result:', result)
    assert result == {
        'name': u'John Doe',
        'values': [
            {'val': u'one'},
            {'val': u'two'},
            {'val': u'three'},
        ],
    }


def test_formset_dict_delete_form():

    class FormAddress(f.Form):
        email = f.Text(validate=[f.ValidEmail])
        etype = f.Text()

    class FormUser(f.Form):
        name = f.Text()
        addresses = f.FormSet(FormAddress, parent='user')

    input_data = {
        'name': u'John Doe',
        'addresses.1-email': u'one@example.com',
        'addresses.2-email': u'two@example.com',
        'addresses.2-etype': u'special',
        'addresses.3-email': u'three@example.com',
    }
    obj_data = {
        'name': u'Foo Bar',
        'addresses': [
            {
                'email': u'1@example.com',
                'etype': u'meh',
            },
            {
                'email': u'2@example.com',
                'etype': u'meh',
            },
            {
                'email': u'3@example.com',
                'etype': u'meh',
            },
        ],
    }
    form = FormUser(input_data, obj_data)

    assert form.save() == {
        'name': u'John Doe',
        'addresses': [
            {
                'email': u'one@example.com',
                'etype': u'meh',
            },
            {
                'email': u'two@example.com',
                'etype': u'special',
            },
            {
                'email': u'three@example.com',
                'etype': u'meh',
            },
        ],
    }


def test_formset_names():
    class MyForm(f.Form):
        a = f.Text(validate=[f.Required])
        b = f.Text(validate=[f.Required])

    class WrapForm(f.Form):
        subs = f.FormSet(MyForm)

    form = WrapForm({})
    print('# form.subs.form.a.name ==', form.subs.form.a.name)
    assert form.subs.form.a.name == 'subs.1-a'

    form = WrapForm({}, {'a': 'foo', 'b': 'bar'})
    print('# form.subs.form.a.name ==', form.subs.form.a.name)
    assert form.subs.form.a.name == 'subs.1-a'

    form = WrapForm({'subs.1-a': 'foo', 'subs.1-b': 'bar'})
    print('# form.subs.form.a.name ==', form.subs.form.a.name)
    print('# form.subs._forms[0].a.name ==', form.subs._forms[0].a.name)
    assert form.subs.form.a.name == 'subs.1-a'
    assert form.subs._forms[0].a.name == 'subs.1-a'


if __name__ == '__main__':
    test_formset_names()
