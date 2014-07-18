.. :changelog:

=============
History
=============

2.x
+++++++++++++++++++++++++++++++++++++

* Selects (and MultiSelects) can take groups of items and render them as ``<optgroup>`` or ``<fieldset>``.

* The ``clean`` and `vprepare`` methods of a field can now be defined as a form method with the signature ``clean_fieldname(py_value, **kwargs)`` and ``prepare_fieldname(obj_value, **kwargs)``.

* Added ``prepare`` and ``clean`` methods to the form so a user can overwrite them to store there the logic of pre and post-processing the data, keeping that logic in the form itself instead of in a view.

* Several bugfixes

