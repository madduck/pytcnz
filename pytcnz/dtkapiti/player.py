# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import re

from ..datarecord import Placeholder
from ..phonenumber import PhoneNumber
from ..squashnz.player import Player as BasePlayer


class Player(BasePlayer):

    class DrawPatternError(BaseException):
        pass

    def __init__(
        self,
        id,
        name,
        gender,
        points,
        dob,
        phone,
        mobile,
        *,
        drawnamepat=r"\w\d{1}",
        **kwargs,
    ):
        draw_name, seed = None, None
        if id is not None and len(id):
            pat = re.compile(rf"(?P<draw>{drawnamepat})(?P<seed>\d+)")
            m = re.match(pat, id)
            if not m:
                raise Player.DrawPatternError(
                    f"Cannot deduce draw/seed from player ID {id}. "
                    f"Maybe the pattern is wrong: {drawnamepat}"
                )
            md = m.groupdict()
            draw_name = md.get("draw")
            seed = int(md.get("seed"))

        kwargs = kwargs | dict(
            draw=Placeholder(name=draw_name),
            seed=seed,
        )

        try:
            phone = PhoneNumber(str(phone))
        except PhoneNumber.InvalidPhoneNumber:
            phone = None
        try:
            mobile = PhoneNumber(str(mobile))
        except PhoneNumber.InvalidPhoneNumber:
            mobile = None

        if dob == "(invalid date )":
            dob = None

        super().__init__(
            id=id,
            name=name,
            gender=gender,
            points=points,
            dob=dob,
            phone=phone,
            mobile=mobile,
            **kwargs,
        )

    def has_defaulted(self):
        return self.get("default", "N").upper() == "Y"


if __name__ == "__main__":
    player = Player("M12", "Martin", "M", 2870, "1979-02-14", "", "021-123456")
    print(player.__dict__)
    print(repr(player))
    try:
        import ipdb

        ipdb.set_trace()
    except ImportError:
        pass
