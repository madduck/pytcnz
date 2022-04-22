# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pyexcel
from ..datasource import DataSource
from .player import Player


class RegistrationsReader(DataSource):
    def __init__(self, filename, *, Player_class=None, **kwargs):
        self.__open_book(filename)
        super().__init__(Player_class=Player_class or Player, **kwargs)

    def __open_book(self, filename):
        self.__filename = filename
        self.__book = pyexcel.get_book(file_name=filename)

    def read_players(
        self, *, colmap=None, resolve_duplicate_cb=None, **kwargs
    ):
        colmap = colmap or {}

        def preprocess(data):
            data["id"] = data[""]
            del data[""]

        rows = self.__book["Registrations"]
        rows.name_columns_by_row(0)
        super().read_players(
            rows.colnames,
            rows,
            colmap=colmap,
            preprocess=preprocess,
            resolve_duplicate_cb=resolve_duplicate_cb,
            **kwargs
        )

    def read_tournament_name(self):
        raise NotImplementedError(
            "Extracted registrations provide no tournament name"
        )

    def read_draws(self, *, colmap=None, **kwargs):
        raise NotImplementedError(
            "Extracted registrations provide no draw data"
        )

    def read_games(self, *, colmap=None, **kwargs):
        raise NotImplementedError(
            "Extracted registrations provide no game data"
        )

    def read_all(self, *, players_colmap=None):
        self.read_players(colmap=players_colmap)
