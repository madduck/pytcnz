# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import re
from .exceptions import BaseException
from .playerbase import PlayerBase
from .draw import Draw as DrawBase
from .game import Game as GameBase


class DataSource:
    class DataUnavailableError(BaseException):
        pass

    class DataAlreadyReadError(BaseException):
        pass

    class DuplicateColumnError(BaseException):
        pass

    class ReadError(BaseException):
        pass

    def __init__(
        self,
        *,
        read_all=False,
        Player_class=PlayerBase,
        Draw_class=DrawBase,
        Game_class=GameBase,
    ):
        self.tname = None
        self.Draw_class = Draw_class
        self.draws = {}
        self.Player_class = Player_class
        self.players = {}
        self.Game_class = Game_class
        self.games = {}
        if read_all:
            self.read_all()

    def __repr__(self):
        r = f"<{self.__class__.__name__}("
        if self.tname:
            r += f'"{self.tname}" '
        r += f"draws:{len(self.draws)} "
        r += f"games:{len(self.games)} "
        r += f"players:{len(self.players)}"
        return f"{r})>"

    @classmethod
    def sanitise_colname(cls, colname):
        def replace_safe(s):
            if s[0].startswith(" "):
                return "_"  # noqa:E271,E701,E501
            elif s[0].isnumeric():
                return f"numeric_{s[0]}"  # noqa:E272,E701,E501
            else:
                return ""  # noqa:E272,E701,E501

        return re.sub(r"^\d+|\W+", replace_safe, str(colname)).lower()

    @classmethod
    def sanitise_colnames(cls, colnames):
        return [cls.sanitise_colname(c) for c in colnames]

    @classmethod
    def apply_colmap(cls, colmap, colnames):
        ret = []
        for col in colnames:
            seen = {}
            while True:
                if col in colmap:
                    seen[col] = True
                    newname = cls.sanitise_colname(colmap[col])
                    if newname in seen:
                        raise DataSource.DuplicateColumnError(
                            f"Infinite recursion in colmap between {col} "
                            f"and {newname}"
                        )
                    elif newname in colnames and newname not in colmap:
                        raise DataSource.DuplicateColumnError(
                            f"Cannot rename {col} to {newname}, already used."
                        )
                    col = newname

                else:
                    ret.append(col)
                    break
        return ret

    def set_tournament_name(self, tname):
        self.tname = tname

    @classmethod
    def read_rows_into(
        cls,
        target,
        colnames,
        rows,
        Klass,
        *,
        colmap=None,
        idcol="name",
        preprocess=None,
        postprocess=None,
        **kwargs,
    ):
        colnames = cls.sanitise_colnames(colnames)
        idcol = cls.sanitise_colname(idcol)
        if colmap:
            colnames = cls.apply_colmap(colmap, colnames)
        for row in rows:
            data = dict(zip(colnames, row))

            if preprocess:
                preprocess(data)

            if not data[idcol]:
                continue

            p = Klass(**data | kwargs)

            if postprocess:
                postprocess(p)

            target[p[idcol]] = p

        return colnames

    def read_players(
        self,
        colnames,
        rows,
        *,
        colmap=None,
        preprocess=None,
        postprocess=None,
        **kwargs,
    ):
        if self.players:
            raise DataSource.DataAlreadyReadError("Players already read")
        try:
            DataSource.read_rows_into(
                self.players,
                colnames,
                rows,
                self.Player_class,
                colmap=colmap,
                preprocess=preprocess,
                postprocess=postprocess,
                **kwargs,
            )
        except BaseException as e:
            raise DataSource.ReadError(f"While reading players: {e}")

    def read_draws(
        self,
        colnames,
        rows,
        *,
        colmap=None,
        preprocess=None,
        postprocess=None,
        **kwargs,
    ):
        if self.draws:
            raise DataSource.DataAlreadyReadError("Draws already read")
        try:
            DataSource.read_rows_into(
                self.draws,
                colnames,
                rows,
                self.Draw_class,
                colmap=colmap,
                preprocess=preprocess,
                postprocess=postprocess,
                **kwargs,
            )
        except BaseException as e:
            raise DataSource.ReadError(f"While reading draws: {e}")

    def read_games(
        self,
        colnames,
        rows,
        *,
        colmap=None,
        preprocess=None,
        postprocess=None,
        **kwargs,
    ):
        if self.games:
            raise DataSource.DataAlreadyReadError("Games already read")
        try:
            DataSource.read_rows_into(
                self.games,
                colnames,
                rows,
                self.Game_class,
                colmap=colmap,
                preprocess=preprocess,
                postprocess=postprocess,
                **kwargs,
            )
        except BaseException as e:
            raise DataSource.ReadError(f"While reading games: {e}")

    def read_all(
        self, *, draws_colmap=None, players_colmap=None, games_colmap=None
    ):
        self.read_tournament_name()
        self.read_draws(colmap=draws_colmap)
        self.read_players(colmap=players_colmap)
        self.read_games(colmap=games_colmap)

    def get_tournament_name(self):
        return self.tname

    def get_games(self):
        return self.games.values()

    def get_draws(self):
        return self.draws.values()

    def get_players(self):
        return self.players.values()
