# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.dtkapiti.draw import Draw
from pytcnz.dtkapiti.player import Player
from .test_draw import make_draw_data
from .test_dtkapiti_player import make_player_data


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


def test_init_colour_conversion(draw):
    assert draw.colour == "563412"


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


def test_add_player_not_seeded(draw):
    unseeded = Player(**make_player_data(id='W00'))
    with pytest.raises(Draw.InvalidPlayerError):
        draw.add_player(unseeded)


def test_numeric_colour(draw_data):
    d = Draw(**draw_data | dict(colour=611651))
    assert d.colour == "511661"
