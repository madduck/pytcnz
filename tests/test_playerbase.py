# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.gender import Gender
from pytcnz.playerbase import PlayerBase as Player

PLAYER = dict(name="Jane Doe", gender=Gender.W)


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


@pytest.fixture(params=["gender", "name"])
def attr_to_check(request):
    return request.param


def test_init_player_missing_data(player_data, attr_to_check):
    del player_data[attr_to_check]
    with pytest.raises(TypeError):
        Player(**player_data)


def test_player_str_gives_name(player_data):
    assert str(Player(**player_data)) == player_data["name"]


def test_player_equality(player, player_data):
    p1 = Player(**player_data)
    assert p1 == player


def test_player_inequality(player, player_data):
    player_data["gender"] = "M"
    p1 = Player(**player_data)
    assert not (p1 == player)


def test_player_sort_order(player, player_data):
    player_data["name"] = "Kate"
    p1 = Player(**player_data)
    assert player < p1
