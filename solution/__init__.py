# -*- coding: utf-8 -*-
"""
Solution
====================

Makes SQLAlchemy easy and fun to use, and adds some custom capabilities.

Example:

.. sourcecode:: python

    from solution import SQLALchemy

    db = SQLALchemy('postgresql://scott:tiger@localhost:5432/mydatabase')

    class ToDo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(60), nullable=False)
        done = db.Column(db.Boolean, nullable=False, default=False)
        pub_date = db.Column(db.DateTime, nullable=False,
            default=datetime.utcnow)

    to_do = ToDo(title='Install Solution', done=True)
    db.add(to_do)
    db.commit()

    completed = db.query(ToDo).filter(ToDo.done == True).all()

It does an automatic table naming (if no name is defined) and, to the
base query class, it adds the following methods::

- first_or_notfound
- get_or_notfound
- to_json

---------------------------------------
MIT License (http://www.opensource.org/licenses/mit-license.php).
Copyright © 2011 by Lúcuma labs (http://lucumalabs.com).  
See `AUTHORS.md` for more details.
"""
from __future__ import absolute_import

import os
import re
import threading

try:
    import sqlalchemy
except ImportError:
    raise ImportError('Unable to load the sqlalchemy package.'
        ' `Solution` needs the SQLAlchemy library to run.'
        ' You can get download it from http://www.sqlalchemy.org/'
        ' If you\'ve already installed SQLAlchemy, then make sure you have '
        ' it in your PYTHONPATH.')
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

from . import fixtures
from .query import Query, Future, NotFound
from .serializers import to_json
from .custom_types import JSONEncodedType


__version__ = '1.5.1'


def _create_scoped_session(db):
    return scoped_session(sessionmaker(autocommit=False, autoflush=True,
        bind=db.engine, query_cls=Query))


def _make_table(db):
    def table_maker(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[2:]
        return sqlalchemy.Table(*args, **kwargs)
    return table_maker


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))
    obj.Table = _make_table(obj)


class _EngineConnector(object):

    def __init__(self, sqlalch):
        self._sqlalch = sqlalch
        self._engine = None
        self._connected_for = None
        self._lock = threading.Lock()

    def get_engine(self):
        with self._lock:
            uri = self._sqlalch.uri
            info = self._sqlalch.info
            options = self._sqlalch.options
            echo = options.get('echo')
            if (uri, echo) == self._connected_for:
                return self._engine
            self._engine = engine = sqlalchemy.create_engine(info, **options)
            self._connected_for = (uri, echo)
            return engine


_CAMELCASE_RE = re.compile(r'([A-Z]+)(?=[a-z0-9])')


class _ModelTableNameDescriptor(object):

    def __get__(self, obj, type):
        tablename = type.__dict__.get('__tablename__')
        if not tablename:
            def _join(match):
                word = match.group()
                if len(word) > 1:
                    return ('_%s_%s' % (word[:-1], word[-1])).lower()
                return '_' + word.lower()
            tablename = _CAMELCASE_RE.sub(_join, type.__name__).lstrip('_')
            setattr(type, '__tablename__', tablename)
        return tablename


class Model(object):
    """Baseclass for custom user models."""

    __tablename__ = _ModelTableNameDescriptor()
    
    def __iter__(self):
        """Returns an iterable that supports .next()
        so we can do dict(sa_instance).
        """
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                yield (k, getattr(self, k))
    
    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def to_dict(self):
        return dict([(k, getattr(self, k)) for k in self.__dict__.keys()
            if not k.startswith('_')])
    
    def to_json(self):
        return to_json(self.to_dict())


class SQLAlchemy(object):
    """This class is used to instantiate a SQLAlchemy connection to
    a database.

        db = SQLAlchemy(_uri_to_database_)

    Additionally this class also provides access to all the SQLAlchemy
    functions from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.
    So you can declare models like this::

        class User(db.Model):
            login = db.Column(db.String(80), unique=True)
            passw_hash = db.Column(db.String(80))

    ∫In a web application you need to call `db.session.remove()`
    after each response, and `db.session.rollback()` if an error occurs.
    
    If your application object has a `after_request` decorator, you can
    fo it automatically binding it::

        app = Shake(settings)
        db = SQLAlchemy('sqlite://', app=app)

    or::

        db = SQLAlchemy()

        app = Shake(settings)
        db.init_app(app)

    """
    
    JSONEncodedType = JSONEncodedType

    def __init__(self, uri='sqlite://', app=None, echo=False, pool_size=None,
            pool_timeout=None, pool_recycle=None):
        self.uri = uri
        self.info = make_url(uri)

        self.options = self.build_options_dict(echo=echo, pool_size=pool_size,
            pool_timeout=pool_timeout, pool_recycle=pool_recycle)
        self.apply_driver_hacks()
        
        self.connector = None
        self._engine_lock = threading.Lock()
        self.session = _create_scoped_session(self)

        self.Model = declarative_base(cls=Model, name='Model')
        self.Model.db = self
        
        if app is not None:
            self.init_app(app)
        
        _include_sqlalchemy(self)

    def apply_driver_hacks(self):
        if self.info.drivername == 'mysql':
            self.info.query.setdefault('charset', 'utf8')
            self.options.setdefault('pool_size', 10)
            self.options.setdefault('pool_recycle', 7200)
        
        elif self.info.drivername == 'sqlite':
            pool_size = self.options.get('pool_size')
            if self.info.database in (None, '', ':memory:') and pool_size == 0:
                raise RuntimeError('SQLite in-memory database with an '
                    'empty queue (pool_size = 0) is not possible due to '
                    'data loss.')

    def build_options_dict(self, **kwargs):
        options = {'convert_unicode': True}
        for key, value in kwargs.items():
            if value is not None:
                options[key] = value
        return options

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup. In a web application or a multithreaded
        environment, never use a database without initialize it first, 
        or connections will leak.
        """
        if not hasattr(app, 'databases'):
            app.databases = []
        if isinstance(app.databases, list):
            if self in app.databases:
                return
            app.databases.append(self)

        def shutdown_session(response=None):
            self.session.remove()
            return response

        def rollback(error=None):
            try:
                self.session.rollback()
            except (Exception), e:
                pass

        if hasattr(app, 'after_request'):
            app.after_request(shutdown_session)
        elif hasattr(app, 'before_response'):
            app.before_response(shutdown_session)
        if hasattr(app, 'on_exception'):
            app.on_exception(rollback)
    
    @property
    def query(self):
        return self.session.query
    
    def add(self, *args, **kwargs):
        return self.session.add(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.session.flush(*args, **kwargs)
    
    def commit(self):
        return self.session.commit()
    
    def rollback(self):
        return self.session.rollback()
    
    @property
    def metadata(self):
        """Returns the metadata"""
        return self.Model.metadata

    @property
    def engine(self):
        """Gives access to the engine. """
        with self._engine_lock:
            connector = self.connector
            if connector is None:
                connector = _EngineConnector(self)
                self.connector = connector
            return connector.get_engine()
    
    def create_all(self):
        """Creates all tables. """
        self.Model.metadata.create_all(bind=self.engine)
    
    def drop_all(self):
        """Drops all tables. """
        self.Model.metadata.drop_all(bind=self.engine)

    def reflect(self, meta=None):
        """Reflects tables from the database. """
        meta = meta or MetaData()
        meta.reflect(bind=self.engine)
        return meta

    def dump_data(self, fixtures_path=fixtures.FIXTURES_PATH, models=None):
        _models = self.Model.__subclasses__()
        if models:
            models = map(str.lower, models)
            _models = [m for m in _models if m.__name__.lower() in models]
        models = _models
        fixtures.dump_data(self, models, fixtures_path)

    def load_data(self, fixtures_path=fixtures.FIXTURES_PATH, models=None):
        _models = self.Model.__subclasses__()
        if models:
            models = map(str.lower, models)
            _models = [m for m in _models if m.__name__.lower() in models]
        models = _models
        fixtures.load_data(self, models, fixtures_path)
        self.session.commit()

    def load_media(self, fixtures_path=fixtures.FIXTURES_PATH):
        fixtures.load_media(fixtures_path)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.uri)

