# -*- coding: utf-8 -*-
from __future__ import absolute_import

try: 
    import simplejson as json
except ImportError:
    import json
from sqlalchemy.types import TypeDecorator, Text


class JSONEncodedType(TypeDecorator):
    """Represents an immutable structure as a JSON-encoded string.
    """

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        try:
            json_value = json.dumps(value)
        except ValueError:
            json_value = {}
        return json_value

    def process_result_value(self, json_value, dialect):
        if json_value is None:
            return {}
        try:
            value = json.loads(json_value)
        except ValueError:
            value = {}
        return value
    
    def copy(self):
          return self.__class__()

