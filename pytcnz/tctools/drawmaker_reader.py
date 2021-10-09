# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pyexcel
from ..datasource import DataSource
from ..gender import Gender
from .player import Player
from .draw import Draw


class ReaderBase(DataSource):
    def __init__(
        self,
        filename,
        *,
        add_players_to_draws=False,
        Draw_class=None,
        Player_class=None,
        **kwargs,
    ):
        self.__open_book(filename)
        self.__add_players_to_draws = add_players_to_draws
        self.__player_sheets = {}
        super().__init__(
            Player_class=Player_class or Player,
            Draw_class=Draw_class or Draw,
            **kwargs,
        )

    def __open_book(self, filename):
        self.__filename = filename
        self.__book = pyexcel.get_book(file_name=filename)

    def __get_player_sheets(self):
        for gender in (Gender.W, Gender.M):
            sheet = self.__player_sheets.get(gender)
            if not sheet:
                name = self.get_player_sheet_name(gender)
                sheet = self.__book[name]
                labelrow = self.get_player_column_label_row(gender)
                sheet.name_columns_by_row(labelrow - 1)
                self.__player_sheets[gender] = sheet
        return self.__player_sheets

    def read_tournament_name(self):
        rows = self.__book["Info"]
        self.set_tournament_name(rows[3, 2])

    def read_draws(self, *, colmap=None, **kwargs):
        read = {}
        for gender, sheet in self.__get_player_sheets().items():
            firstrow = self.get_first_player_data_row(gender)
            for rowx in range(firstrow - 1, sheet.number_of_rows()):
                d = sheet[rowx, "Draw"]
                if d in read:
                    continue
                read[d] = None
        super().read_draws(
            ["name"], [[d] for d in read.keys()], colmap=colmap, **kwargs
        )

    def read_players(self, *, colmap=None, **kwargs):
        postprocess = None
        if self.__add_players_to_draws:
            if not self.draws:
                raise DataSource.DataUnavailableError(
                    "add_players_to_draws: Draws have not been read"
                )

            def postprocess(p):
                self.__add_player_to_draw(p)

        combined = []
        for gender, sheet in self.__get_player_sheets().items():
            firstrow = self.get_first_player_data_row(gender)
            for rowx in range(firstrow - 1, sheet.number_of_rows()):
                row = sheet.row[rowx]
                row.append(gender)
                combined.append(row)

        colnames = DataSource.sanitise_colnames(sheet.colnames)
        colnames.append("gender")

        def preprocess(data):
            for field in self.remove_fields:
                if field in data:
                    del data[field]
            self.preprocess_player_data(data)

        super().read_players(
            colnames,
            combined,
            colmap=colmap,
            preprocess=preprocess,
            postprocess=postprocess,
            **kwargs,
        )

    def __add_player_to_draw(self, player):
        self.draws[player.draw.name].add_player(player)

    def add_players_to_draws(self):
        if not self.draws:
            raise DataSource.DataUnavailableError(
                "add_players_to_draws: Draws have not been read"
            )

        for player in self.players.values():
            self.__add_player_to_draw(player)

    def read_games(self, *, colmap=None, **kwargs):
        raise NotImplementedError("DrawMaker provides no game data")

    def read_all(self, *, draws_colmap=None, players_colmap=None):
        self.read_tournament_name()
        self.read_draws(colmap=draws_colmap)
        self.read_players(colmap=players_colmap)


class DrawMakerReader(ReaderBase):
    def __init__(
        self,
        filename,
        *,
        add_players_to_draws=False,
        Draw_class=None,
        Player_class=None,
        **kwargs,
    ):

        self.remove_fields = {
            "male",
            "female",
            "male1",
            "female1",
            "r",
            "w",
            "source",
            "phoneraw",
            "mobileraw",
            "email_to",
            "comments1",
            "",
        }
        self.__per_draw_counter = {}

        super().__init__(
            filename,
            add_players_to_draws=add_players_to_draws,
            Draw_class=Draw_class,
            Player_class=Player_class,
            **kwargs,
        )

    def read_players(self, *, colmap=None, **kwargs):
        colmap = (colmap or {}) | dict(
            name1="isquash_name",
            phone="phoneraw",
            phnormal="phone",
            mobile="mobileraw",
            mobnormal="mobile",
        )
        super().read_players(colmap=colmap, **kwargs)

    def get_player_sheet_name(self, gender):
        if gender == Gender.W:
            return "Women"  # noqa:E271,E701
        elif gender == Gender.M:
            return "Men"  # noqa:E271,E701

    def get_player_column_label_row(self, gender):
        return 2

    def get_first_player_data_row(self, gender):
        # do not add +1 since the column label row is not counted
        return self.get_player_column_label_row(gender)

    def preprocess_player_data(self, data):
        for k, v in data.copy().items():
            if k.startswith("numeric_"):
                if k[8] != "0":
                    # the column title is actually the sum of draw assignments
                    if data["wl"] and len(str(v)) == 0:
                        # waitlisted
                        v = "-"
                    data["draw"] = f"{data['gender'].name}{v}"
                else:
                    del data[k]

        d = data.setdefault("draw", "X-")
        seed = self.__per_draw_counter.get(d, 0) + 1
        self.__per_draw_counter[d] = seed
        data["seed"] = seed


class DrawsReader(ReaderBase):
    def __init__(
        self,
        filename,
        *,
        add_players_to_draws=False,
        Draw_class=None,
        Player_class=None,
        **kwargs,
    ):

        self.remove_fields = {
            "",
            "men",
            "women",
            "age",
            "first_name",
            "email_to",
            "wed",
            "wed1",
            "wed2",
            "thu",
            "thu1",
            "thu2",
            "thu3",
            "fri",
            "fri1",
            "fri2",
            "fri3",
            "sat",
            "sat1",
            "sat2",
            "sat3",
            "numeric_0",
            "size",
        }

        super().__init__(
            filename,
            add_players_to_draws=add_players_to_draws,
            Draw_class=Draw_class,
            Player_class=Player_class,
            **kwargs,
        )

    def get_player_sheet_name(self, gender):
        if gender == Gender.W:
            return "Women's Draws"  # noqa:E271,E701
        elif gender == Gender.M:
            return "Men's Draws"  # noqa:E271,E701

    def get_player_column_label_row(self, gender):
        return 8

    def get_first_player_data_row(self, gender):
        # do not add +1 since the column label row is not counted
        return self.get_player_column_label_row(gender)

    def preprocess_player_data(self, data):
        pass
