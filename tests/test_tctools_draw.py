# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.tctools.draw import Draw
from .test_draw import make_draw_data
from pytcnz.tctools.player import Player
from .test_tctools_player import make_player_data


@pytest.fixture
def player():
    return Player(**make_player_data())


@pytest.fixture
def draw_data():
    return make_draw_data(**dict(desc="Women's Open", colour="$00123456"))


def test_init(draw_data):
    Draw(**draw_data)


@pytest.fixture
def draw(draw_data):
    return Draw(**draw_data)


def test_auto_description_open(draw):
    assert draw.description == "Women's Open"


def test_auto_description_div1(draw_data):
    assert Draw(**draw_data | dict(name="W1")).description == "Women's Div 1"


def test_add_player(draw, player):
    draw.add_player(player)


def test_add_player_duplicate(draw, player):
    draw.add_player(player)
    with pytest.raises(Draw.DuplicatePlayerError):
        draw.add_player(player)


def test_add_player_not_matching_draw(draw_data, player):
    draw = Draw(**draw_data | dict(name="M3"))
    with pytest.raises(Draw.InvalidPlayerError):
        draw.add_player(player)
