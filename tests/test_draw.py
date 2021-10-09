# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
import pytest
from pytcnz.draw import Draw
from pytcnz.gender import Gender


DRAW = dict(name="W0", gendered="W")


def make_draw_data(**data):
    return DRAW | data


@pytest.fixture
def draw_data():
    return make_draw_data()


def test_init_draw(draw_data):
    Draw(**draw_data)


@pytest.fixture
def draw(draw_data):
    return Draw(**draw_data)


def test_init_draw_missing_data(draw_data):
    del draw_data["name"]
    with pytest.raises(TypeError):
        return Draw(**draw_data)


def test_draw_str_gives_name(draw_data):
    assert str(Draw(**draw_data)) == draw_data["name"]


@pytest.fixture
def draw_m0():
    return Draw(**make_draw_data(name="M0"))


def test_women_first_sort_order(draw, draw_m0):
    assert draw < draw_m0


@pytest.fixture
def draw_m0_chauvi():
    return Draw(**make_draw_data(name="M0", ladies_first=False))


def test_women_first_disabled_sort_order(draw, draw_m0_chauvi):
    assert not (draw < draw_m0_chauvi)


@pytest.fixture(
    params=[
        "M",
        "W",
        "Man",
        "Men",
        "Women",
        "Woman",
        "male",
        "female",
        None,
        Gender.M,
        Gender.W,
        Gender.N,
    ]
)
def valid_gender(request):
    return request.param


def test_valid_genders(valid_gender):
    Draw(**make_draw_data(gendered=valid_gender))
