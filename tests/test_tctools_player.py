# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest
from pytcnz.tctools.player import Player
from pytcnz.gender import Gender

PLAYER = dict(
    draw="W0",
    seed=1,
    name="Jane Doe",
    gender=Gender.W,
    points=3050,
    dob="30-Aug-1999",
    wl=False,
    number="021234567",
)


def make_player_data(**data):
    return PLAYER | data


@pytest.fixture
def player_data():
    return make_player_data()


def test_player_init(player_data):
    Player(**player_data)


@pytest.fixture
def player(player_data):
    return Player(**player_data)


def test_parse_draw(player):
    assert player.draw.name == PLAYER["draw"]


def test_parse_seed(player):
    assert player.seed == PLAYER["seed"]


@pytest.fixture(
    params=["draw", "seed", "name", "gender", "points", "dob", "wl", "number"]
)
def attr_to_check(request):
    return request.param


def test_init_player_missing_data(player_data, attr_to_check):
    del player_data[attr_to_check]
    with pytest.raises(TypeError):
        Player(**player_data)


def test_player_wl(player):
    assert not player.wl


def test_player_has_id(player):
    assert len(player.id) > 0


def test_player_strict_invalid_phonenumber(player_data):
    with pytest.raises(Player.InvalidPhoneNumber):
        Player(strict=True, **player_data | dict(number="041234567"))


def test_player_relaxed_invalid_phonenumber(player_data):
    Player(strict=False, **player_data | dict(number="041234567"))
