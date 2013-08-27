# -*- coding: utf-8 -*-
"""
=========
Solution
=========

An amazing form solution.

* Return validated data as dictionaries or create/update a linked model and child models.
* Sub-forms and form sets
* Extremely flexible in the field representation (altough with default HTML representation that might be good enough).
* Easy individual field or form-wide validators.
* Customizable cleanup functions.


`MIT License <http://www.opensource.org/licenses/mit-license.php>`_
© `Lúcuma labs <http://lucumalabs.com>`_

"""
from .form import Form
from .formset import FormSet
from .fields import *
from .validators import *
from .utils import Markup, get_html_attrs, to_unicode


__version__ = '2.4.4'

