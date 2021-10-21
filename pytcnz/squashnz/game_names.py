# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

GAME_NAMES_BY_DRAW_SIZE = {
    6: {
        "401": ("Championship Final", "Final"),
        "402": ("Plate Final", "Plate"),
    },
    8: {
        "301": ("Championship Final", "Final"),
        "302": ("Special Plate Final", "Sp.Plate"),
        "303": ("Special Plate Final", "Plate"),
        "304": ("Special Plate Final", "Co.Plate"),
    },
}


def get_game_name(drawsize, gamecode, *, short=False):
    names = GAME_NAMES_BY_DRAW_SIZE.get(drawsize)
    if not names:
        return gamecode
    name = names.get(gamecode)
    if name:
        return name[1 if short else 0]
    else:
        return gamecode