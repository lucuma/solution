# -*- coding: utf-8 -*-
from __future__ import absolute_import

import threading

try:
    from shake import NotFound
except ImportError:
    class NotFound(Exception):
        pass

from sqlalchemy.orm.query import Query as BaseQuery

from .serializers import to_json


class Query(BaseQuery):
    """The subtype of :class:`sqlalchemy.orm.query.Query` class, that provides
    custom methods.
    """

    def first_or_notfound(self):
        """Like :meth:`first` but if no result is found, instead of
        returning `None` raises a NotFound exception.
        """
        result = self.first()
        if result is None:
            raise NotFound
        return result
    
    def get_or_notfound(self, ident):
        """Like :meth:`get` but aborts with 404 if not found instead of
        returning `None`.
        """
        result = self.get(ident)
        if result is None:
            raise NotFound
        return result
    
    def promise(self):
        """Makes a promise and returns a :class:`Future`.
        """
        return Future(self)
    
    def to_json(self):
        return to_json([dict(item) for item in self])


class Future(object):
    """Promised future query result.

    :param query: the query to promise
    :type query: :class:`sqlalchemy.orm.query.Query`

    Copied from SQLAlchemy-Future, written by Hong Minhee.
    http://lunant.github.com/SQLAlchemy-Future/
    Used under the MIT license.
    """

    __slots__ = "query", "_iter", "_head", "_thread"

    def __init__(self, query):
        self.query = query
        self._iter = None
        self._head = None
        thread_name = "{0}-{1}".format(type(self).__name__, id(self))
        self._thread = threading.Thread(target=self.execute_promise,
            name=thread_name)
        self._thread.start()

    def execute_promise(self):
        self._iter = iter(self.query)
        try:
            val = self._iter.next()
        except StopIteration:
            self._head = ()
        else:
            self._head = val,

    def __iter__(self):
        if self._iter is None or self._head is None:
            self._thread.join()
        if not self._head:
            return
        yield self._head[0]
        for value in self._iter:
            yield value

    def all(self):
        """Returns the results promised as a :class:`list`. This blocks the
        underlying execution thread until the execution has finished if it
        is not yet.
        """
        return list(self)

