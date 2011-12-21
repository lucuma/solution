
Shake-SQLAlchemy
====================

Implements a bridge to SQLAlchemy, adding some custom capabilities.

To the base model class:

    - Automatic table naming
    - to_dict method + iterable
    - to_json method

To the base query class, the following methods:

    - to_json
    - first_or_notfound
    - get_or_notfound
    - promise
