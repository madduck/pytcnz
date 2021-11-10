# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import pyexcel
import xlrd.compdoc
from ..datasource import DataSource
from ..exceptions import BaseException
from .player import Player
from .game import Game
from .draw import Draw


class TCExportReader(DataSource):
    class IncompatibleFileError(BaseException):
        pass

    def __init__(
        self,
        filename,
        *,
        add_players_to_draws=False,
        add_games_to_draws=False,
        add_players_to_games=False,
        autoflip_scores=False,
        Draw_class=None,
        Game_class=None,
        Player_class=None,
        **kwargs
    ):
        self.__open_book(filename)
        self.__add_players_to_draws = add_players_to_draws
        self.__add_games_to_draws = add_games_to_draws
        self.__add_players_to_games = add_players_to_games
        self.__autoflip_scores = autoflip_scores
        super().__init__(
            Player_class=Player_class or Player,
            Draw_class=Draw_class or Draw,
            Game_class=Game_class or Game,
            **kwargs
        )

    def __open_book(self, filename):
        self.__filename = filename
        try:
            self.__book = pyexcel.get_book(file_name=filename)
        except xlrd.compdoc.CompDocError as e:
            if "size exceeds expected" in e.args[0]:
                raise TCExportReader.IncompatibleFileError(
                    "{filename} is corrupt, open and save it with "
                    "LibreOffice to fix"
                )
            else:
                raise

    def read_tournament_name(self):
        rows = self.__book["Tournament"]
        rows.name_rows_by_column(0)
        self.set_tournament_name(rows["Title", 0])

    def read_draws(self, *, colmap=None, **kwargs):
        rows = self.__book["Draws"]
        rows.name_columns_by_row(0)
        super().read_draws(rows.colnames, rows, colmap=colmap, **kwargs)

    def read_players(self, *, colmap=None, **kwargs):
        postprocess = None
        if self.__add_players_to_draws:
            if not self.draws:
                raise DataSource.DataUnavailableError(
                    "add_players_to_draws: Draws have not been read"
                )

            def postprocess(p):
                if p.draw.name:
                    self.__add_player_to_draw(p)

        colmap = colmap or {}
        colmap |= dict(code="id")

        rows = self.__book["Players"]
        rows.name_columns_by_row(0)
        super().read_players(
            rows.colnames,
            rows,
            colmap=colmap,
            postprocess=postprocess,
            **kwargs
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

    def read_games(self, *, colmap=None, autoflip_scores=None, **kwargs):
        preprocess, postprocess = None, None

        if self.__add_players_to_games:
            if not self.players:
                raise DataSource.DataUnavailableError(
                    "add_players_to_games: Players have not been read"
                )

            preprocess = lambda g: self.__replace_player_names_with_records(g)

        if self.__add_games_to_draws:
            if not self.draws:
                raise DataSource.DataUnavailableError(
                    "add_games_to_draws: Draws have not been read"
                )

            postprocess = lambda g: self.__add_game_to_draw(g)

        autoflip_scores = (
            autoflip_scores
            if autoflip_scores is not None
            else self.__autoflip_scores
        )

        rows = self.__book["Games"]
        rows.name_columns_by_row(0)
        super().read_games(
            rows.colnames,
            rows,
            colmap=colmap,
            preprocess=preprocess,
            postprocess=postprocess,
            autoflip_scores=autoflip_scores,
            **kwargs
        )

    def __add_game_to_draw(self, game):
        self.draws[game.draw.name].add_game(game)

    def __replace_player_names_with_records(self, gamedata):
        for p in (1,2):
            if player := gamedata[f'player{p}']:
                gamedata[f'player{p}'] = self.players[player]

    def add_games_to_draws(self):
        if not self.draws:
            raise DataSource.DataUnavailableError(
                "add_games_to_draws: Draws have not been read"
            )

        for game in self.games.values():
            self.__add_game_to_draw(game)

    def add_players_to_games(self):
        if not self.players:
            raise DataSource.DataUnavailableError(
                "add_players_to_games: Players have not been read"
            )

        for game in self.games.values():
            self.__add_game_to_draw(game)

    def get_played_games(self):
        return [
            g
            for g in self.games.values()
            if g.status <= Game.Status.justfinished
        ]

    def get_pending_games(self):
        return [
            g
            for g in self.games.values()
            if g.status > Game.Status.justfinished
        ]
