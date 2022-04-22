# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
import pytest

from pytcnz.game import Game
from pytcnz.scores import Scores

GAME = dict(name="W0101", player1="Jane", player2="Kate")


def make_game_data(**data):
    return GAME | data


@pytest.fixture
def game_data():
    return make_game_data()


def test_init_game(game_data):
    Game(**game_data)


@pytest.fixture
def game(game_data):
    return Game(**game_data)


@pytest.fixture(params=["name", "player1", "player2"])
def attr_to_check(request):
    return request.param


def test_init_game_missing_data(game_data, attr_to_check):
    del game_data[attr_to_check]
    with pytest.raises(TypeError):
        return Game(**game_data)


def test_game_str_gives_name(game_data):
    assert str(Game(**game_data)) == game_data["name"]


def test_known_player(game_data):
    g = Game(**game_data)
    assert g.is_player_known(Scores.Player.A)


def test_unknown_player(game_data):
    g = Game(**game_data | dict(player1=""))
    assert not g.is_player_known(Scores.Player.A)


def test_sort_order(game_data, game):
    assert Game(**game_data | dict(name="M0101")) < game
