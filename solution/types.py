# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sqlalchemy.types import TypeDecorator, Text

from .serializers import to_json, from_json


class JSONEncodedType(TypeDecorator):
    """Represents an immutable structure as a JSON-encoded string.
    """
    
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        try:
            json_value = to_json(value)
        except ValueError:
            json_value = {}
        return json_value

    def process_result_value(self, json_value, dialect):
        if json_value is None:
            return {}
        try:
            value = from_json(json_value)
        except ValueError:
            value = {}
        return value
    
    def copy(self):
          return self.__class__()

