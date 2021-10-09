# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import enum
import re
from datetime import date
import dateutil.parser
from ..playerbase import PlayerBase
from ..phonenumber import PhoneNumber
from ..exceptions import InvalidDataError
from .grading import SquashNZGrading


class Player(PlayerBase):
    class InvalidPhoneNumber(InvalidDataError):
        pass

    class AgeGroup(enum.IntEnum):
        Master = 35  # noqa:E221
        Senior = 19  # noqa:E221
        Junior = 0  # noqa:E221,E222
        Unknown = -1  # noqa:E221

        def __str__(self):
            return self.name

    def __init__(
        self,
        *,
        name,
        points,
        gender,
        grade=None,
        dob=None,
        onday=None,
        strict=True,
        **kwargs,
    ):
        data = kwargs.copy()

        first_name = Player.get_first_name(name)
        age_group = Player.AgeGroup.Unknown
        age = None

        if dob:
            try:
                dob.strftime("")
            except AttributeError:
                dob = dateutil.parser.parse(dob, dayfirst=True)

            age = Player.get_age_for_dob(dob, onday=onday)
            age_group = Player.get_age_group_for_age(age)

        if grade and grade.startswith("J"):
            age_group = Player.AgeGroup.Junior

        grading = SquashNZGrading(
            points, gender, age_group == Player.AgeGroup.Junior
        )

        data.update(
            first_name=first_name,
            points=grading.points,
            grade=grading.grade,
            grading=grading,
            age_group=age_group,
            age=age,
            dob=dob,
        )

        for nr in ("phone", "mobile"):
            try:
                number = data.get(nr)
                if number:
                    data[nr] = PhoneNumber(str(number))
            except PhoneNumber.InvalidPhoneNumber:
                if strict:
                    raise Player.InvalidPhoneNumber(
                        f"{number} does not appear to be a valid phone number"
                    )
                else:
                    pass

        super().__init__(name=name, gender=gender, **data)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.name} ({self.age_group}) "
            f"{self.grade} @ {self.points:,d} pts)>"
        )

    @classmethod
    def get_age_for_dob(cls, dob, *, onday=None):
        onday = onday or date.today()
        return (
            onday.year
            - dob.year
            - ((onday.month, onday.day) < (dob.month, dob.day))
        )

    def get_age(self, *, onday=None):
        return Player.get_age_for_dob(self.dob, onday=onday)

    @classmethod
    def get_age_group_for_age(cls, age):
        for th in list(Player.AgeGroup):
            if age >= th:
                return th

    def get_age_group(self, *, onday=None):
        age = self.get_age(onday=onday)
        return Player.get_age_group_for_age(age)

    SALUTATIONS = ("Mr", "Mrs", "Ms", "Miss", "Dr")

    @classmethod
    def get_first_name(cls, name, *, ignore_salutations=None):
        ignore_salutations = ignore_salutations or cls.SALUTATIONS
        pat = (
            rf"^(?:(?:{'|'.join(ignore_salutations)})\.?\s*)*"
            r"(?P<fname>\S+).+"
        )
        match = re.match(pat, name)
        try:
            return match["fname"]
        except IndexError:
            raise Player.NameParseError(
                f"Failed to determine first name of {name}"
            )


if __name__ == "__main__":
    player1 = Player(
        name="Martin Krafft",
        gender="M",
        points=2870,
        dob="1979-02-14",
        mobile="021-234567",
        id=14,
    )
    player2 = Player(
        name="Jane Doe", gender="f", points=900, grade="J1", code="WNTHJXD"
    )

    print(vars(player1))
    print(repr(player1))
    print()
    print(vars(player2))
    print(repr(player2))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
