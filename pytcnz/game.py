# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
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
        if self.get("reverse_name_sort", True) and other.get(
            "reverse_name_sort", True
        ):
            # The "better" games usually have a lower number, e.g. M0301 is
            # the final, and M0304 is the consolation plate, and the "better"
            # games are generally later, so sort them in reverse order
            return other.name.__lt__(self.name)
        else:
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
