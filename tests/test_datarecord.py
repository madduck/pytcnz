# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
import pytest

from pytcnz.datarecord import DataRecord, Placeholder


def test_init():
    DataRecord()


def test_init_data():
    DataRecord(one=1, two=2, three=3)


@pytest.fixture
def data_record():
    return DataRecord(one=1, two=2, Three=3)


def test_data_access(data_record):
    assert data_record["one"] == 1
    assert data_record.get("one") == 1


def test_data_access_default(data_record):
    assert data_record.get("four", 4) == 4


def test_data_access_missing(data_record):
    with pytest.raises(KeyError):
        data_record["four"]


def test_data_check_attr(data_record):
    assert hasattr(data_record, "one")


def test_data_check_attr_missing(data_record):
    assert not hasattr(data_record, "four")


def test_data_check_item(data_record):
    assert "one" in data_record


def test_data_check_item_missing(data_record):
    assert "four" not in data_record


def test_data_readonly(data_record):
    with pytest.raises(DataRecord.ReadOnlyError):
        data_record["four"] = 4


def test_cannot_update(data_record):
    with pytest.raises(DataRecord.ReadOnlyError):
        data_record.update(dict(four=4))


def test_cannot_delete(data_record):
    with pytest.raises(DataRecord.ReadOnlyError):
        del data_record["two"]


def test_attribute_access(data_record):
    assert data_record.two == 2


def test_attribute_access_missing(data_record):
    with pytest.raises(AttributeError):
        data_record.four


def test_attribute_access_readonly(data_record):
    with pytest.raises(DataRecord.ReadOnlyError):
        data_record.four = 4


def test_reserved_names():
    with pytest.raises(DataRecord.InvalidDataError):
        DataRecord(data="data")


def test_key_names_lowercase_item(data_record):
    assert data_record["three"] == 3
    assert "Three" not in data_record


def test_placeholder_init_noname():
    with pytest.raises(TypeError):
        Placeholder()


def test_placeholder_init():
    Placeholder(name="foo")


def test_placeholder_morph():
    rec = DataRecord()
    p = Placeholder(name="foo")
    p.set(rec)
    assert p == rec
