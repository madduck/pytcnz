# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest
from pytcnz.dtkapiti.player import Player
from pytcnz.gender import Gender

PLAYER = {
    "id": "W01",
    "name": "Jane Doe",
    "gender": Gender.W,
    "grading_code": "WNTHJXD",
    "points": 3050,
    "grade": "A2",
    "club": "Thorndon",
    "dob": "30/08/1999",
    "phone": "041234567",
    "mobile": "021234567",
    "email": "jane.doe@example.org",
    "comment": "comment",
    "paid": "1",
    "method": "method",
    "default": "default",
}


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
    assert player.draw.name == PLAYER["id"][:2]


def test_parse_seed(player):
    assert player.seed == int(PLAYER["id"][2:])


def test_parse_big_draw(player_data):
    draw = "M00"
    seed = 4
    _id = f"{draw}{seed}"
    p = Player(drawnamepat=r"\w\d{2}", **player_data | dict(id=_id))
    assert p.draw.name == draw
    assert p.seed == seed


@pytest.fixture(params=["id", "gender", "points", "dob", "phone", "mobile"])
def attr_to_check(request):
    return request.param


def test_init_player_missing_data(player_data, attr_to_check):
    del player_data[attr_to_check]
    with pytest.raises(TypeError):
        Player(**player_data)
