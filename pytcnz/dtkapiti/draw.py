# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..draw import Draw as BaseDraw
from ..exceptions import BaseException


class Draw(BaseDraw):
    class InvalidGameError(BaseException):
        pass

    class InvalidPlayerError(BaseException):
        pass

    class DuplicateGameError(BaseException):
        pass

    class DuplicatePlayerError(BaseException):
        pass

    @classmethod
    def delphi_colour_to_rgb(cls, c):
        # Delphi stores colours in reverse order to RGB
        return f"{c[7:]}{c[5:7]}{c[3:5]}"

    def __init__(self, name, *, gendered=None, **kwargs):
        self.players = []
        self.games = []

        data = kwargs.copy()
        colour = data.get("colour")
        if colour:
            data["colour"] = Draw.delphi_colour_to_rgb(colour)
        else:
            data["colour"] = "FFFFFF"

        super().__init__(name=name, **data)

    def add_player(self, player):
        if not player.id.startswith(self.name):
            raise Draw.InvalidPlayerError(
                f"Player {player} does not belong into draw {self.name}"
            )

        if player in self.players:
            raise Draw.DuplicatePlayerError(
                f"Player {player} already added to draw {self.name}"
            )

        if player.seed <= 0:
            raise Draw.InvalidPlayerError(
                f"Player {player} has invalid seeding {player.seed} in draw "
                f"{self.name}"
            )

        for i in range(max(0, player.seed - len(self.players))):
            self.players.append(None)
        player.draw.set(self)
        self.players[player.seed - 1] = player

    def get_players(self):
        return self.players

    def add_game(self, game):
        if not game.name.startswith(self.name):
            raise Draw.InvalidGameError(
                f"Game {game} does not belong into draw {self.name}"
            )

        if game in self.games:
            raise Draw.DuplicateGameError(
                f"Game {game} already added to draw {self.name}"
            )

        game.draw.set(self)
        self.games.append(game)

    def get_games(self):
        return self.games


if __name__ == "__main__":
    from ..gender import Gender

    d = Draw(
        "W0", description="Women's Open", gendered=Gender.N, colour="$00123456"
    )
    print(vars(d))
    print(repr(d))
    try:
        import ipdb

        ipdb.set_trace()
    except ImportError:
        pass
