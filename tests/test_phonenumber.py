# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.phonenumber import PhoneNumber


@pytest.fixture(
    params=[
        ("042234567", False),
        ("021234567", True),
        ("0274656789", True),
    ]
)
def is_mobile_pair(request):
    return request.param


def test_check_mobile(is_mobile_pair):
    assert (
        PhoneNumber(is_mobile_pair[0]).is_mobile_number() == is_mobile_pair[1]
    )


@pytest.fixture(
    params=[
        "029123456",
        "028123455",
        "023212321",
        "041212324",
        "6441212324",
        "5271234",
    ]
)
def incomplete_number(request):
    return request.param


def test_incomplete_number(incomplete_number):
    with pytest.raises(PhoneNumber.InvalidPhoneNumber):
        PhoneNumber(incomplete_number)
