# -*- coding: utf-8 -*-


class FakeMultiDict(dict):
    """Adds a fake `getlist` method to a regular dict; or act as a proxy to
    Webob's MultiDict `getall` method. 
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError, error:
            raise AttributeError(error)

    def getlist(self, name):
        if hasattr(self, 'getall'):
            return self.getall(name)
        value = self.get(name)
        if value is None:
            return []
        return [value]
