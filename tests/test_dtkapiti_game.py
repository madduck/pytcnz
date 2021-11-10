# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.scores import Scores
from pytcnz.dtkapiti.game import Game
from .test_game import make_game_data


@pytest.fixture
def game_data():
    return make_game_data(
        from1="",
        from2="",
        score1=0,
        score2=0,
        status=99,
        comment="a comment",
        daytime="Thu 18:00",
    )


@pytest.fixture
def played_game_data(game_data):
    return game_data | dict(score1=1, status=0, comment="11-0 11-0 11-0")


def test_init(game_data):
    Game(**game_data)


def test_init_game_ref1(game_data):
    g = Game(**game_data | dict(player1="", from1="W W0101"))
    assert isinstance(g.player1, Game.Reference)


def test_init_game_ref2(game_data):
    g = Game(**game_data | dict(player2="", from2="W W0101"))
    assert isinstance(g.player2, Game.Reference)


@pytest.fixture
def game(game_data):
    return Game(**game_data)


def test_parse_draw(game, game_data):
    assert game.draw.name == game_data["name"][:2]


def test_parse_big_draw(game_data):
    draw = "M00"
    g = Game(drawnamepat=r"\w\d{2}", **game_data | dict(name=draw))
    assert g.draw.name == draw


def test_ref_means_unknown_player(game_data):
    g = Game(**game_data | dict(from2="W W0101", player2=""))
    assert not g.is_player_known(Scores.Player.B)


def test_no_scores_unless_played(game_data):
    g = Game(**game_data)
    assert g.scores is None


def test_played_no_winner(game_data):
    with pytest.raises(Game.InconsistentResultError):
        Game(**game_data | dict(status=0))


@pytest.fixture
def played_game(played_game_data):
    return Game(**played_game_data)


def test_scores_parsed(played_game):
    assert isinstance(played_game.scores, Scores)


def test_scores_parsed_comment(played_game_data):
    c = "a comment"
    g = Game(
        **played_game_data
        | dict(comment=f'{played_game_data["comment"]}  {c}')
    )
    assert g.comment == c


def test_scores_parsed_no_comment(played_game):
    assert played_game.comment == ""


def test_inconsistent_no_winner(played_game_data):
    with pytest.raises(Game.InconsistentResultError):
        Game(**played_game_data | dict(score1=0))


def test_inconsistent_both_winners(played_game_data):
    with pytest.raises(Game.InconsistentResultError):
        Game(**played_game_data | dict(score2=1))


def test_inconsistent_scores_disagree(played_game_data):
    with pytest.raises(Game.InconsistentResultError):
        Game(**played_game_data | dict(status=0, score1=0, score2=1))


def test_inconsistent_scores_autoflip(played_game_data):
    g = Game(
        **played_game_data
        | dict(status=0, score1=0, score2=1, autoflip_scores=True)
    )
    assert g.get_scores().winner == Scores.Player.B


def test_no_datetime_sort(game_data):
    unscheduled = Game(**game_data | dict(daytime=None))
    assert Game(**game_data | dict(daytime="Fri 18:00")) < unscheduled


def test_sort_order_days(game_data):
    assert Game(**game_data) < Game(**game_data | dict(daytime="Fri 18:00"))


def test_no_datetime_is_none(game_data):
    assert Game(**game_data | dict(daytime=None)).datetime is None


def test_sort_order_same_time(game_data):
    assert not (Game(**game_data) < Game(**game_data))


def test_game_day_sort_no_date(game_data):
    gd1 = Game(**game_data | dict(name="W0101", daytime=""))
    gd2 = Game(**game_data | dict(name="W1101", daytime=""))
    assert gd1 < gd2


def test_game_day_sort_same_time_reverse(game_data):
    final = Game(**game_data | dict(name="W0301", daytime="Sat 18:00"))
    plate = Game(**game_data | dict(name="W0303", daytime="Sat 18:00"))
    assert plate < final


def test_fancy_game_name_round1(game):
    assert game.get_fancy_name() == game.name


def test_fancy_game_name_round3_no_drawsize(game_data):
    final = Game(**game_data | dict(name="W0301"))
    assert final.get_fancy_name() == final.name


def test_fancy_game_name_round3_8draw(game_data):
    final = Game(**game_data | dict(name="W0301"))
    assert final.get_fancy_name(drawsize=8) == "Championship Final"


@pytest.mark.xfail  # TODO expected to fail until we resolve BYE/defaults
def test_game_with_defaulted_player(game_data):
    g = Game(**game_data | dict(status=-1))


def test_is_scheduled(game):
    assert game.is_scheduled()


def test_is_played(played_game):
    assert played_game.is_played()
