# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
import pytest

from pytcnz.squashnz.grading import SquashNZGrading


@pytest.fixture(
    params=[
        ("W", False, 3500, "A1"),
        ("W", False, 2870, "A2"),
        ("W", False, 1430, "D1"),
        ("W", False, 590, "F"),  # noqa:E202
        ("W", True, 590, "J1"),
        ("W", True, 250, "J3"),
        ("M", False, 4500, "A1"),
        ("M", False, 2980, "B2"),
        ("M", False, 1430, "E1"),
        ("M", False, 690, "F"),  # noqa:E202
        ("M", True, 690, "J2"),
        ("M", True, 250, "J4"),
        ("N", False, 250, "Ungraded"),
        ("N", True, 250, "Ungraded"),
        ("N", False, 3000, "Ungraded"),
        ("N", True, 3000, "Ungraded"),
    ]
)
def grading_tuplets(request):
    return request.param


def test_init(grading_tuplets):
    gender, junior, points, grade = grading_tuplets
    g = SquashNZGrading(points, gender, junior)
    assert g.grade == grade


@pytest.fixture
def grading():
    return SquashNZGrading(2870, "M")


def test_int_gives_points(grading):
    assert int(grading) == grading.points


def test_str_gives_grade(grading):
    assert str(grading) == grading.grade


grading2 = grading


def test_equality(grading, grading2):  # noqa:E302
    assert grading == grading2


def test_sort_order_equal(grading, grading2):
    assert not (grading < grading2)


@pytest.fixture
def another_grading(grading_tuplets):
    gender, junior, points, grade = grading_tuplets
    return SquashNZGrading(points, gender, junior)


def test_equality_all_unequal(grading, another_grading):
    assert grading != another_grading


@pytest.fixture(params=["M", "W"])
def lower_grading(request):
    return SquashNZGrading(2780, request.param)


def test_sort_order_different_genders(lower_grading, grading):
    assert lower_grading < grading


@pytest.fixture(params=[-1, 0])
def invalid_points(request):
    return request.param


def test_invalid_points(invalid_points):
    with pytest.raises(SquashNZGrading.InvalidGradingError):
        SquashNZGrading(invalid_points, "W")
