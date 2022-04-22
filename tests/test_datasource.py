# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.datasource import DataSource


def test_colmap():
    cols = ["red", "green", "blue"]
    colmap = dict(red="yellow")
    cols = DataSource.apply_colmap(colmap, cols)
    assert cols[0] == "yellow"


def test_colmap_recursive():
    cols = ["red", "green", "blue"]
    colmap = dict(red="yellow", yellow="pink")
    cols = DataSource.apply_colmap(colmap, cols)
    assert cols[0] == "pink"


def test_colmap_conflict():
    cols = ["red", "green", "blue"]
    colmap = dict(red="yellow", yellow="green")
    with pytest.raises(DataSource.DuplicateColumnError):
        DataSource.apply_colmap(colmap, cols)


def test_colmap_infinite():
    cols = ["red", "green", "blue"]
    colmap = dict(red="yellow", yellow="red")
    with pytest.raises(DataSource.DuplicateColumnError):
        DataSource.apply_colmap(colmap, cols)


def test_colmap_non_string():
    cols = ["red", "green", "blue"]
    colmap = dict(red=3)
    ret = DataSource.apply_colmap(colmap, cols)
    assert ret[0] == DataSource.sanitise_colname((colmap[cols[0]]))


@pytest.fixture(
    params=[
        ("with space", "with_space"),
        ("UpperCase", "uppercase"),
        ("123", "numeric_123"),
        ("12startswithnumber", "numeric_12startswithnumber"),
    ]
)
def colname_pairs(request):
    return request.param


def test_colname_sanitisation(colname_pairs):
    assert DataSource.sanitise_colname(colname_pairs[0]) == colname_pairs[1]


TEST_DATA = [
    ["int", "name", "str", "upper"],
    [1, "one", "1", "ONE"],
    [2, "two", "2", "TWO"],
    [3, "three", "3", "THREE"],
]


@pytest.fixture
def colnames():
    return TEST_DATA[0][:]


@pytest.fixture
def rows():
    return TEST_DATA[1:][:]


def test_read_rows_return(colnames, rows):
    target = {}
    ret = DataSource.read_rows_into(target, colnames, rows, dict)
    assert ret == colnames


def test_read_rows_length(colnames, rows):
    target = {}
    DataSource.read_rows_into(target, colnames, rows, dict)
    assert len(target) == len(rows)


def test_read_rows_dcols(colnames, rows):
    target = {}
    DataSource.read_rows_into(target, colnames, rows, dict)
    for row in rows:
        assert row[1] in target


def test_read_rows_data(colnames, rows):
    target = {}
    DataSource.read_rows_into(target, colnames, rows, dict)
    for row in rows:
        assert set(target[row[1]].values()) == set(row)


def test_read_rows_other_idcol(colnames, rows):
    target = {}
    DataSource.read_rows_into(target, colnames, rows, dict, idcol="upper")
    for row in rows:
        assert set(target[row[3]].values()) == set(row)


def test_read_rows_other_idcol_sanitised(colnames, rows):
    target = {}
    DataSource.read_rows_into(target, colnames, rows, dict, idcol="UPPER")
    for row in rows:
        assert set(target[row[3]].values()) == set(row)


def test_read_rows_resolv_duplicate_callback(colnames, rows):
    target = {}

    fake_row = [33, 'three', '33', 'I am pretending to be three']
    rows.append(fake_row)

    def resolve_cb(existing, new):
        # override default policy, which would be that new replaces old
        return existing

    DataSource.read_rows_into(target, colnames, rows, dict,
                              resolve_duplicate_cb=resolve_cb)

    # assert that new did not replace old
    assert target['three'] != fake_row


def test_read_rows_preprocess(colnames, rows):
    target = {}
    status = dict(preprocess=False)

    def preprocess(data):
        for colname in colnames:
            assert colname in data
        status["preprocess"] = True

    DataSource.read_rows_into(
        target, colnames, rows, dict, preprocess=preprocess
    )
    assert status["preprocess"]


def test_read_rows_postprocess(colnames, rows):
    target = {}
    status = dict(postprocess=False)

    def postprocess(data):
        for colname in colnames:
            assert colname in data
        status["postprocess"] = True

    DataSource.read_rows_into(
        target, colnames, rows, dict, postprocess=postprocess
    )
    assert status["postprocess"]


def test_read_rows_colname_sanitisation(colnames, rows):
    target = {}
    colnames[0] = "1"
    ret = DataSource.read_rows_into(target, colnames, rows, dict)
    assert ret[0] == DataSource.sanitise_colname(colnames[0])


def test_read_rows_colmap_application(colnames, rows):
    target = {}
    colmap = dict(str="string")

    ret = DataSource.read_rows_into(
        target, colnames, rows, dict, colmap=colmap
    )
    assert colmap["str"] in ret


def test_read_rows_colmap_sanitisation(colnames, rows):
    target = {}
    colmap = dict(str=3)

    ret = DataSource.read_rows_into(
        target, colnames, rows, dict, colmap=colmap
    )
    assert DataSource.sanitise_colname(colmap["str"]) in ret


@pytest.fixture(params=["players", "draws", "games"])
def read_function_name(request):
    return request.param


@pytest.fixture
def datasource():
    return DataSource(Player_class=dict, Draw_class=dict, Game_class=dict)


def test_read_functions(colnames, rows, read_function_name, monkeypatch):
    obj = object()

    def read_into_mock(self, colnames, rows, Klass, **kwargs):
        self[read_function_name] = obj
        return colnames

    monkeypatch.setattr(DataSource, "read_rows_into", read_into_mock)

    ds = DataSource()
    fn = getattr(ds, f"read_{read_function_name}")
    fn(colnames, rows)
    fn = getattr(ds, f"get_{read_function_name}")
    assert list(fn())[0] == obj


def test_read_functions_not_twice(
    colnames, rows, read_function_name, datasource
):
    fn = getattr(datasource, f"read_{read_function_name}")
    fn(colnames, rows)
    with pytest.raises(DataSource.DataAlreadyReadError):
        fn(colnames, rows)


def test_set_tournament_name(datasource):
    tname = "foo"
    datasource.set_tournament_name(tname)
    assert datasource.get_tournament_name() == tname


def test_read_rows_data(colnames, rows):
    target = {}
    DataSource.read_rows_into(target, colnames, rows, dict, additional="data")
    assert target["one"]["additional"] == "data"
