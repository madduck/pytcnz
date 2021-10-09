# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..datarecord import Placeholder
from ..phonenumber import PhoneNumber
from ..squashnz.player import Player as BasePlayer
import re


class Player(BasePlayer):
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
            md = re.match(pat, id).groupdict()
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


if __name__ == "__main__":
    player = Player("M12", "Martin", "M", 2870, "1979-02-14", "", "021-123456")
    print(player.__dict__)
    print(repr(player))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
