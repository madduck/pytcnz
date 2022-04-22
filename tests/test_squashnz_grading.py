# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
import pytest

from pytcnz.squashnz.grading import SquashNZGrading


@pytest.fixture(
    params=[
        ("W", False, 3500, "A1"),
        ("W", False, 2870, "A2"),
        ("W", False, 1430, "D1"),
        ("W", False, 590, "F"),
        ("W", True, 590, "J1"),
        ("W", True, 250, "J3"),
        ("W", False, 0, "Ungraded"),
        ("W", True, 0, "Ungraded"),
        ("M", False, 4500, "A1"),
        ("M", False, 2980, "B2"),
        ("M", False, 1430, "E1"),
        ("M", False, 690, "F"),
        ("M", True, 690, "J2"),
        ("M", True, 250, "J4"),
        ("M", False, 0, "Ungraded"),
        ("M", True, 0, "Ungraded"),
        ("N", False, 0, "Ungraded"),
        ("N", True, 0, "Ungraded"),
        ("N", False, 2000, "Ungraded"),
        ("N", True, 2000, "Ungraded"),
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


@pytest.fixture(
    params=[
        ("W", False, -1),
        ("W", False, 100),
        ("W", True, -1),
        ("W", True, 1),
        ("M", False, -1),
        ("M", False, 500),
        ("M", True, -1),
        ("M", True, 50),
    ]
)
def invalid_points(request):
    return request.param


def test_invalid_points(invalid_points):
    gender, junior, points = invalid_points
    with pytest.raises(SquashNZGrading.InvalidGradingError):
        SquashNZGrading(points, gender, junior)

@pytest.fixture(
    params=[
        ("W", 50, "J4"),
        ("W", 250, "J3"),
        ("W", 450, "J2"),
        ("W", 550, "J1"),
        ("W", 600, "E"),
        ("M", 250, "J4"),
        ("M", 450, "J3"),
        ("M", 650, "J2"),
        ("M", 850, "J1"),
        ("M", 900, "E2"),
    ]
)
def junior_tuplet(request):
    return request.param

def test_junior_transition(junior_tuplet):
    gender, points, grade = junior_tuplet
    g = SquashNZGrading(points, gender, True)
    assert g.grade == grade
