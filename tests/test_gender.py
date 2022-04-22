# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.gender import Gender, InvalidGenderError


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
        "NONE",
        "N",
        "w",
        "m",
        "f",
    ]
)
def valid_gender(request):
    return request.param


def test_valid_genders(valid_gender):
    Gender.from_string(valid_gender)


@pytest.fixture(params=[1, "X", True, "bar"])
def invalid_gender(request):
    return request.param


def test_invalid_genders(invalid_gender):
    with pytest.raises(InvalidGenderError):
        Gender.from_string(invalid_gender)


@pytest.fixture(
    params=[(Gender.M, "Male"), (Gender.W, "Female"), (Gender.N, "None")]
)
def gender_sex_pair(request):
    return request.param


def test_gender_to_sex_conversion(gender_sex_pair):
    assert Gender.to_sex(gender_sex_pair[0]) == gender_sex_pair[1]
