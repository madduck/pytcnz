# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest
from datetime import date

from pytcnz.squashnz.player import Player
from .test_playerbase import PLAYER

PLAYER = PLAYER | dict(
    id=14,
    squash_code="WNTHJXD",
    points=3050,
    dob="1-Sep-1999",
    phone="043841234",
    mobile="021234567",
    email="jane.doe@example.org",
    comment="player comment",
)


def make_player_data(**kwargs):
    return PLAYER | kwargs


@pytest.fixture
def player_data():
    return make_player_data()


def test_init_player(player_data):
    Player(**player_data)


@pytest.fixture
def player(player_data):
    return Player(**player_data)


@pytest.fixture(params=["gender", "name", "points"])
def attr_to_check(request):
    return request.param


def test_init_player_missing_data(player_data, attr_to_check):
    del player_data[attr_to_check]
    with pytest.raises(TypeError):
        Player(**player_data)


def test_player_age(player):
    assert player.get_age(onday=date(2021, 10, 6)) == 22


def test_player_age_group(player):
    assert (
        player.get_age_group(onday=date(2021, 10, 6)) == Player.AgeGroup.Senior
    )


def test_player_age_no_dob(player):
    player = Player(**make_player_data(dob=None))
    assert player.age is None
    assert player.age_group == Player.AgeGroup.Unknown


def test_player_age_group_junior(player_data):
    player = Player(**player_data | dict(grade="J1"))
    assert player.age_group == Player.AgeGroup.Junior


def test_player_strict_invalid_phonenumber(player_data):
    with pytest.raises(Player.InvalidPhoneNumber):
        Player(strict=True, **player_data | dict(phone="041234567"))


def test_player_relaxed_invalid_phonenumber(player_data):
    Player(strict=False, **player_data | dict(phone="041234567"))


@pytest.fixture(
    params=[
        ("Jane Doe", "Jane"),
        ("Ms. Jane Doe", "Jane"),
        ("Carry-Ann Doe", "Carry-Ann"),
        ("John A. Doe", "John"),
        ("John Alfred Doe", "John"),
        ("Dr. John Doe", "John"),
    ]
)
def name_and_firstname(request):
    return request.param


def test_first_name_extraction(player_data, name_and_firstname):
    player_data["name"] = name_and_firstname[0]
    p = Player(**player_data)
    assert p.first_name == name_and_firstname[1]
