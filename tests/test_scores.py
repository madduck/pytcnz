# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
import pytest
from pytcnz.scores import Scores

A = Scores.Player.A
B = Scores.Player.B

VALID_BESTOF5 = [
    ([(11, 3), (11, 8), (11, 8)], A),
    ([(0, 11), (11, 4), (11, 8), (11, 3)], A),
    ([(9, 11), (6, 11), (13, 11), (14, 12), (13, 11)], A),
]
INVALID_BESTOF5 = [
    ([], A),
    ([(11, 3)], A),
    ([(9, 11), (6, 11), (13, 11), (14, 12)], None),
    ([(11, 1), (11, 1), (11, 1), (11, 1)], A),
    ([(11, 1), (11, 1), (11, 1), (11, 1), (11, 1)], A),
    ([(11, 1), (11, 1), (11, 1), (11, 1), (11, 1), (11, 1)], A),
    ([(9, 11), (6, 11), (13, 11), (14, 12), (11, 13), (11, 13)], B),
]
INVALID_BESTOF5_BUT_3 = [
    ([(11, 3), (11, 8)], A),
]
VALID_BESTOF3 = [
    ([(3, 11), (8, 11)], B),
    ([(11, 3), (11, 8), (8, 11)], A),
]
INVALID_BESTOF3_BUT_5 = [
    ([(6, 11), (5, 11), (4, 11)], B),
    ([(6, 11), (11, 5), (7, 11), (5, 11)], B),
]
INVALID_BESTOF3 = [
    ([], A),
    ([(11, 3)], A),
    ([(11, 3), (8, 11)], None),
]


@pytest.fixture(params=VALID_BESTOF3)
def valid_bestof3(request):
    return request.param


@pytest.fixture(params=VALID_BESTOF5)
def valid_bestof5(request):
    return request.param


@pytest.fixture(params=VALID_BESTOF3 + VALID_BESTOF5)
def valid_bestof3n5(request):
    return request.param


@pytest.fixture(params=INVALID_BESTOF3 + INVALID_BESTOF3_BUT_5)
def invalid_bestof3(request):
    return request.param


@pytest.fixture(params=INVALID_BESTOF5 + INVALID_BESTOF5_BUT_3)
def invalid_bestof5(request):
    return request.param


# the first invalid best-of 3 is a valid best-of 5
@pytest.fixture(params=INVALID_BESTOF3 + INVALID_BESTOF5)
def invalid_bestof3n5(request):
    return request.param


def test_valid_bestof3(valid_bestof3):
    Scores(valid_bestof3[0], bestof=3)


def test_valid_bestof5(valid_bestof5):
    Scores(valid_bestof5[0], bestof=5)


def test_valid_bestof3n5(valid_bestof3n5):
    Scores(valid_bestof3n5[0], bestof=(3, 5))


def test_invalid_bestof3(invalid_bestof3):
    with pytest.raises(Scores.IncompleteError):
        Scores(invalid_bestof3[0], bestof=3)


def test_invalid_bestof5(invalid_bestof5):
    with pytest.raises(Scores.IncompleteError):
        Scores(invalid_bestof5[0], bestof=5)


def test_invalid_bestof3n5(invalid_bestof3n5):
    with pytest.raises(Scores.IncompleteError):
        Scores(invalid_bestof3n5[0], bestof=(3, 5))


VALID_PAR11 = [
    ([(11, 5), (11, 8), (11, 3)], A),
    ([(11, 13), (20, 22), (10, 12)], B),
]
INVALID_PAR11 = [
    ([(11, 10), (11, 0), (11, 0)], A),  # not won by 2
    ([(4, 10), (0, 11), (0, 11)], B),  # not reached 11
    ([(9, 12), (0, 11), (0, 11)], B),  # didn't need to go to 12
]
VALID_PAR15 = [
    ([(15, 5), (15, 8), (15, 3)], A),
    ([(15, 17), (20, 22), (14, 16)], B),
]
INVALID_PAR15 = [
    ([(15, 14), (15, 0), (15, 0)], A),  # not won by 2
    ([(4, 13), (0, 15), (0, 15)], B),  # not reached 15
    ([(4, 11), (0, 15), (0, 15)], B),  # not reached 15 but 11!
    ([(13, 16), (0, 15), (0, 15)], B),  # didn't need to go to 16
]


@pytest.fixture(params=VALID_PAR11)
def valid_par11(request):
    return request.param


@pytest.fixture(params=VALID_PAR15)
def valid_par15(request):
    return request.param


@pytest.fixture(params=VALID_PAR11 + VALID_PAR15)
def valid_par11n15(request):
    return request.param


@pytest.fixture(params=INVALID_PAR11)
def invalid_par11(request):
    return request.param


@pytest.fixture(params=INVALID_PAR15)
def invalid_par15(request):
    return request.param


@pytest.fixture(params=INVALID_PAR11 + INVALID_PAR15)
def invalid_par11n15(request):
    return request.param


def test_valid_par11(valid_par11):
    Scores(valid_par11[0], par=11)


def test_valid_par15(valid_par15):
    Scores(valid_par15[0], par=15)


def test_valid_par11n15(valid_par11n15):
    Scores(valid_par11n15[0], par=(11, 15))


def test_invalid_par11(invalid_par11):
    with pytest.raises(Scores.IncompleteError):
        Scores(invalid_par11[0], par=11)


def test_invalid_par15(invalid_par15):
    with pytest.raises(Scores.IncompleteError):
        Scores(invalid_par15[0], par=15)


def test_invalid_par11n15(invalid_par11n15):
    with pytest.raises(Scores.IncompleteError):
        Scores(invalid_par11n15[0], par=(11, 15))


@pytest.fixture(
    params=[
        "11-6 12-10 11-4",
        "11/4 11-4 11:2",
        "11-6,11-2,11-8",
        "11-8, 11-2, 12-10",
        "11- 8 11 -2 12 - 10",
    ]
)
def valid_string(request):
    return request.param


def test_from_string(valid_string):
    Scores.from_string(valid_string)


@pytest.fixture(
    params=[
        "",
        "No scores, just a comment",
    ]
)
def no_scores_string(request):
    return request.param


def test_from_string_no_scores(no_scores_string):
    scores, remainder = Scores.from_string(no_scores_string)
    assert scores is None
    assert remainder == no_scores_string


def test_from_string_with_comment():
    c = "The Quick Brown Fox Jumped Over The Lazy Dog"
    s, comment = Scores.from_string(f"11-0 11-0 11-0 {c}")
    assert c == comment


@pytest.fixture(params=VALID_PAR11 + VALID_PAR15)
def valid_scores(request):
    return request.param


def test_winner(valid_scores):
    assert Scores(valid_scores[0]).winner == valid_scores[1]


@pytest.fixture(params=["11-4 5-11 11-8 12-10"])
def valid_score(request):
    return Scores.from_string(request.param)[0]


def test_length(valid_score):
    assert len(valid_score) == 4


def test_iteration(valid_score):
    assert list(valid_score)[1] == (5, 11)


def test_flip_scores(valid_score):
    valid_score.flip_scores()
    assert valid_score == Scores.from_string("4-11 11-5 8-11 10-12")[0]
