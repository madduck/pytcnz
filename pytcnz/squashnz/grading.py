# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..exceptions import BaseException
from ..gender import Gender, InvalidGenderError
import enum


class SquashNZGrading:
    class Points_Men(enum.IntEnum):
        A1 = 4000
        A2 = 3500
        B1 = 3100
        B2 = 2700
        C1 = 2400
        C2 = 2100
        D1 = 1800
        D2 = 1500
        E1 = 1200
        E2 = 900
        F = 600
        Ungraded = 0

    class Points_Junior_Men(enum.IntEnum):
        J1 = 700
        J2 = 500
        J3 = 300
        J4 = 100
        Ungraded = 0

    class Points_Women(enum.IntEnum):
        A1 = 3200
        A2 = 2700
        B1 = 2400
        B2 = 2100
        C1 = 1800
        C2 = 1500
        D1 = 1200
        D2 = 900
        E = 600
        F = 300
        Ungraded = 0

    class Points_Junior_Women(enum.IntEnum):
        J1 = 500
        J2 = 300
        J3 = 100
        J4 = 5
        Ungraded = 0

    class Points_Ungendered(enum.IntEnum):
        Ungraded = 0

    class InvalidGradingError(BaseException):
        pass

    @classmethod
    def points_to_grade(cls, points, gender, junior=False):
        if points is None or points < 0:
            raise SquashNZGrading.InvalidGradingError(
                "Points have to be positive"
            )
        try:
            table = {
                (Gender.M, False): cls.Points_Men,
                (Gender.M, True): cls.Points_Junior_Men,
                (Gender.W, False): cls.Points_Women,
                (Gender.W, True): cls.Points_Junior_Women,
                (Gender.N, False): cls.Points_Ungendered,
                (Gender.N, True): cls.Points_Ungendered,
            }[(gender, junior)]
        except KeyError:
            raise InvalidGenderError(
                f"Not a valid gender for grading: {gender.name}"
            )
        for th in list(table):
            if (th != table.Ungraded and points >= th) or (
                th == table.Ungraded and points == th
            ):
                return th

        raise SquashNZGrading.InvalidGradingError(
            f"No grade for {points} points"
        )

    def __init__(self, points, gender, junior=False):
        self._points = points
        self._gender = Gender.from_string(gender)
        self._junior = junior
        self._grade = SquashNZGrading.points_to_grade(
            points, self._gender, junior
        )

    points = property(lambda s: s._points)
    grade = property(lambda s: s._grade.name)
    gender = property(lambda s: s._gender)
    junior = property(lambda s: s._junior)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.gender.name}, "
            f"{self.grade}, {self.points:,d})>"
        )

    def __hash__(self):
        return hash(repr(self))

    def __str__(self):
        return self.grade

    def __eq__(self, other):
        return (
            self.points == other.points
            and self.gender == other.gender
            and self.junior == other.junior
        )

    def __lt__(self, other):
        return self.points.__lt__(other.points)

    def __int__(self):
        return self.points


if __name__ == "__main__":
    grading = SquashNZGrading(2870, "M")
    print(vars(grading))
    print(repr(grading))
    try:
        import ipdb

        ipdb.set_trace()
    except ImportError:
        pass
