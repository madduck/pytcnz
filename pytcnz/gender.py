# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import enum
from .exceptions import BaseException


class InvalidGenderError(BaseException):
    pass


class Gender(enum.Enum):
    M = "Man"
    W = "Woman"
    N = None

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, gender):
        if gender is None:
            return cls.N
        elif gender in list(cls):
            return gender
        else:
            gender = str(gender)[0].upper()
            if gender.startswith("F"):
                gender = "W"  # noqa:E271,E701
            elif gender == "-":
                gender = "N"  # noqa:E271,E701
            try:
                return cls.__members__[gender]
            except KeyError:
                raise InvalidGenderError(f"{gender} is not a valid gender")
