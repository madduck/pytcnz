# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import dateutil.parser
from .datarecord import DataRecord


class Game(DataRecord):
    def __init__(self, name, player1, player2, **kwargs):
        self.players = (player1, player2)
        super().__init__(name=name, player1=player1, player2=player2, **kwargs)

    def __repr__(self):
        s = f"<{self.__class__.__name__}({self.name}"
        s = f'{s}: {" & ".join(map(str, self.players))}'
        return f"{s})>"

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.name.__lt__(other.name)

    def __hash__(self):
        return hash(self.name)

    def is_player_known(self, player):
        return bool(self.players[player])


if __name__ == "__main__":
    gd = dict(name="W0101", player1="Jane", player2="Kate")
    g1 = Game(**gd)
    print(vars(g1))
    print(repr(g1))
    print()
    gd.update(datetime=dateutil.parser.parse("Thu 7:30pm"))
    g2 = Game(**gd)
    print(vars(g2))
    print(repr(g2))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
