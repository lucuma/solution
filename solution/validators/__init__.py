from .validator import Validator
from .simple import Required, IsNumber
from .values import LongerThan, ShorterThan, LessThan, MoreThan, InRange
from .patterns import Match, ValidEmail, ValidURL, IsColor

from .form_wide import FormValidator, AreEqual, AtLeastOne