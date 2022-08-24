# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..draw import Draw as BaseDraw
from ..exceptions import BaseException


class Draw(BaseDraw):
    class InvalidDataError(BaseDraw.InvalidDataError):
        pass

    class InvalidPlayerError(BaseException):
        pass

    class DuplicatePlayerError(BaseException):
        pass

    def __init__(self, name, *, gendered=None, **kwargs):
        self.players = []

        if name[0] == "M":
            desc = "Men's"  # noqa:E701
        elif name[0] == "W":
            desc = "Women's"  # noqa:E701
        else:
            desc = f"{name[0]}"  # noqa:E701

        if name[1] == "O":
            div = 0  # noqa:E701
        else:
            try:
                div = int(name[1:])  # noqa:E701
            except ValueError:
                raise Draw.InvalidDataError(
                    f"Draw number cannot be parsed: {name}"
                )

        if div == 0:
            desc = f"{desc} Open"  # noqa:E701
        else:
            desc = f"{desc} Div {div}"  # noqa:E701

        super().__init__(name=name, description=desc, gendered=gendered)

    def add_player(self, player):
        if not player.id.startswith(self.name):
            raise Draw.InvalidPlayerError(
                f"Player {player} does not belong into draw {self.name}"
            )

        if player in self.players:
            raise Draw.DuplicatePlayerError(
                f"Player {player} already added to draw {self.name}"
            )

        for i in range(max(0, player.seed - len(self.players))):
            self.players.append(None)
        player.draw.set(self)
        self.players[player.seed - 1] = player

    def get_players(self):
        return self.players


if __name__ == "__main__":
    from ..gender import Gender

    d = Draw("W0", gendered=Gender.W)
    print(vars(d))
    print(repr(d))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
