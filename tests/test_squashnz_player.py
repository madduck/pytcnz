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
    vaccinated="X",
    vaccination_expiry="30-Dec-2099",
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


def test_player_get_age_no_dob(player):
    player = Player(**make_player_data(dob=None))
    assert player.get_age() is None
    assert player.get_age_group() == Player.AgeGroup.Unknown


def test_player_age_dob_emptystring(player):
    player = Player(**make_player_data(dob=""))
    assert player.age is None
    assert player.age_group == Player.AgeGroup.Unknown


def test_player_get_age_dob_emptystring(player):
    player = Player(**make_player_data(dob=""))
    assert player.get_age() is None
    assert player.get_age_group() == Player.AgeGroup.Unknown


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
        ("Mrs. Jane Doe", "Jane Doe"),
        ("Ms. Jane Doe", "Jane Doe"),
        ("Miss Carry-Ann Doe", "Carry-Ann Doe"),
        ("Dr. John Doe", "John Doe"),
        ("Mr. John Doe", "John Doe"),
        ("John A. Doe", "John Doe"),
        ("John Alfred Doe", "John Alfred Doe"),
        ("Mrs Jane Doe", "Jane Doe"),
    ]
)
def name_and_cleaned_name(request):
    return request.param


def test_name_cleaning(name_and_cleaned_name):
    assert (
        Player.get_name_cleaned(name_and_cleaned_name[0])
        == name_and_cleaned_name[1]
    )


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


def test_first_name_extraction(name_and_firstname):
    assert (
        Player.get_first_name(name_and_firstname[0]) == name_and_firstname[1]
    )


def test_equality_ignores_id(player_data):
    p1 = Player(**player_data)
    p2 = Player(**player_data | dict(id="foo"))
    assert p1 == p2


def test_single_word_name(player_data):
    p = Player(**player_data | dict(name="Bye"))


def test_vaccination_status(player):
    assert player.is_vaccinated() == Player.VaccinationStatus.V


def test_vaccination_status_bool(player):
    assert player.is_vaccinated()


def test_vaccination_status_no_expiry_bool(player_data):
    p = Player(**player_data | dict(vaccination_expiry=""))
    assert not p.is_vaccinated()


def test_vaccination_status_expired(player):
    assert (
        player.is_vaccinated(onday=date(2099, 12, 31))
        == Player.VaccinationStatus.E
    )


def test_vaccination_status_expired_bool(player):
    assert not player.is_vaccinated(onday=date(2099, 12, 31))


def test_unvaccinated_player(player_data):
    p = Player(**player_data | dict(vaccinated=""))
    assert p.is_vaccinated() == Player.VaccinationStatus.N


def test_unvaccinated_player_bool(player_data):
    p = Player(**player_data | dict(vaccinated=""))
    assert not p.is_vaccinated()
