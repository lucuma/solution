.. :changelog:

History
-------

2.x
+++++++++++++++++++++++++++++++++++++

* Selects (and MultiSelects) can take groups of items and render them as ``<optgroup>`` or ``<fieldset>``.

* The ``clean`` and `vprepare`` methods of a field can now be defined as a form method with the signature ``clean_fieldname(py_value, **kwargs)`` and ``prepare_fieldname(obj_value, **kwargs)``.

* Several bugfixes
