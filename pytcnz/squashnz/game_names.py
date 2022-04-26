# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

GAME_NAMES_BY_DRAW_SIZE = {
    6: {
        "101": ("#1 vs. #6", "1 X 6"),
        "102": ("#2 vs. #5", "2 X 5"),
        "103": ("#3 vs. #4", "3 X 4"),
        "401": ("Championship Final", "Final"),
        "402": ("Plate Final", "Plate"),
    },
    8: {
        "101": ("#1 vs. #8", "1 X 8"),
        "102": ("#4 vs. #5", "4 X 5"),
        "103": ("#3 vs. #6", "3 X 6"),
        "104": ("#2 vs. #7", "2 X 7"),
        "201": ("Semi Final A", "Semi A"),
        "202": ("Semi Final B", "Semi B"),
        "203": ("Plate Semi A", "Pl.Semi A"),
        "204": ("Plate Semi B", "Pl.Semi B"),
        "301": ("Championship Final", "Final"),
        "302": ("Special Plate Final", "Sp.Plate"),
        "303": ("Plate Final", "Plate"),
        "304": ("Consolation Plate Final", "Co.Plate"),
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
