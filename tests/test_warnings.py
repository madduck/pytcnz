# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pytest

from pytcnz.warnings import Warnings, Warning, _Warnings


def test_is_singleton():
    assert Warnings is _Warnings()


def test_add():
    Warnings.add('test')
    assert Warnings[-1] == Warning('test')


def test_clear():
    Warnings.clear()
    assert len(Warnings) == 0


def test_bool():
    Warnings.clear()
    assert not Warnings
    Warnings.add("")
    assert Warnings


def test_skip_duplicates():
    Warnings.clear()
    Warnings.add('test')
    Warnings.add('test')
    assert len(Warnings) == 1
    Warnings.add('test', test_skip_duplicates=False)
    assert len(Warnings) == 2
