# -*- coding: utf-8 -*-
from datetime import datetime
import os
import pytest

from solution import SQLAlchemy, JSONEncodedType, NotFound, Future


prefix = 'sqlite:///'
URI1 = 'db1.sqlite'
URI2 = 'db2.sqlite'


def tear_down():
    try:
        os.remove(URI1)
    except:
        pass
    try:
        os.remove(URI2)
    except:
        pass


def create_test_model(db):

    class Todo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        text = db.Column(db.Text)
        done = db.Column(db.Boolean, nullable=False, default=False)
        pub_date = db.Column(db.DateTime, nullable=False,
            default=datetime.utcnow)
        
        def __init__(self, title, text):
            self.title = title
            self.text = text
    
    return Todo


def test_insert():
    tear_down()
    db = SQLAlchemy(prefix + URI1)
    Todo = create_test_model(db)
    db.create_all()

    def add(title, text=''):
        todo = Todo(title, text)
        db.add(todo)
    
    add('First', 'The text')
    add('Second', 'The text')
    db.commit()
    titles = ' '.join(x.title for x in db.query(Todo).all())
    assert titles == 'First Second'
    tear_down()


def test_select():
    tear_down()
    db = SQLAlchemy(prefix + URI1)
    Todo = create_test_model(db)
    db.create_all()

    data = db.query(Todo).all()
    assert len(data) == 0

    def add(title, text=''):
        todo = Todo(title, text)
        db.add(todo)
    
    add('First', 'The text')
    add('Second', 'The text')
    db.commit()
    
    data = db.query(Todo).all()
    assert len(data) == 2

    data = db.query(Todo).filter(Todo.title == 'First').all()
    assert len(data) == 1

    data = db.query(Todo).filter(Todo.title == 'First').first()
    assert data.title == 'First'
    tear_down()


def test_helper_api():
    db = SQLAlchemy()
    assert db.metadata == db.Model.metadata


def test_notfound():
    tear_down()
    db = SQLAlchemy(prefix + URI1)
    Todo = create_test_model(db)
    db.create_all()
    TITLE = 'test'
    TEXT = 'The text'
    todo = Todo(TITLE, TEXT)
    db.add(todo)
    db.commit()

    with pytest.raises(NotFound):
        db.query(Todo).filter(Todo.title== 'foo').first_or_notfound()
    
    with pytest.raises(NotFound):
        db.query(Todo).get_or_notfound(999)
    
    data = db.query(Todo).filter(Todo.title== TITLE).first_or_notfound()
    assert data.text == TEXT
    tear_down()


def test_multiple_databases():
    tear_down()
    db1 = SQLAlchemy(prefix + URI1)
    db2 = SQLAlchemy(prefix + URI2)
    Todo1 = create_test_model(db1)
    Todo2 = create_test_model(db2)
    db1.create_all()
    db2.create_all()

    def add1(title, text):
        todo1 = Todo1(title, text)
        db1.add(todo1)

    def add2(title, text):
        todo2 = Todo2(title, text)
        db2.add(todo2)

    add1('A', 'a')
    add1('B', 'b')
    add2('Q', 'q')
    add1('C', 'c')
    db1.commit()
    db2.commit()

    assert db1.query(Todo1).count() == 3
    assert db2.query(Todo2).count() == 1
    tear_down()


def test_jsontype():
    tear_down()
    db = SQLAlchemy(prefix + URI1)

    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(JSONEncodedType, nullable=False)
    
    db.create_all()

    data = {'body': 'Hello world', 'number': 5, 'boolean': True}
    post = Post(content=data)
    db.add(post)
    db.commit()
    
    post = db.query(Post).first()
    assert post.content == data
    tear_down()


def test_promises():
    tear_down()
    db = SQLAlchemy(prefix + URI1)
    Todo = create_test_model(db)
    db.create_all()

    def add(title, text=''):
        todo = Todo(title, text)
        db.add(todo)
    
    add('First', 'The text')
    add('Second', 'The text')
    db.commit()

    data = db.query(Todo).promise()
    assert isinstance(data, Future)
    ## Consume the future
    list(data)
    tear_down()

