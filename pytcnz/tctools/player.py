# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from ..datarecord import Placeholder
from ..phonenumber import PhoneNumber
from ..warnings import Warnings
from ..squashnz.player import Player as BasePlayer


class Player(BasePlayer):

    def __init__(
        self,
        *,
        draw,
        seed,
        name,
        gender,
        points,
        dob,
        wl,
        number,
        strict=True,
        **kwargs,
    ):

        data = kwargs | dict(
            number=number,
            draw=Placeholder(name=draw),
            seed=seed,
            id=f"{draw}{seed}",
            wl=bool(wl),
        )

        for nr in ("phone", "mobile", "number"):
            # TODO: fold into super-class
            try:
                number = data.get(nr)
                if number:
                    data[nr] = PhoneNumber(str(number))
            except PhoneNumber.InvalidPhoneNumber:
                msg = f"{number} is not a valid phone number for player {name}"
                if strict:
                    raise BasePlayer.InvalidPhoneNumber(msg)
                else:
                    Warnings.add(msg, context=f"Reading player {name}")

        super().__init__(
            name=name,
            gender=gender,
            points=points,
            dob=dob,
            mobile=number,
            strict=strict,
            **data,
        )

    def __repr__(self):
        r = super().__repr__()[:-2]
        if self.wl:
            r = f"{r}, waitlisted"
        try:
            if not self.available:
                r = f"{r}, unavailable"
        except AttributeError:
            pass
        return f"{r})>"


if __name__ == "__main__":
    player = Player(
        draw="M1",
        seed=2,
        name="Martin",
        gender="M",
        points=2870,
        dob="1979-02-14",
        number="0211100938",
        wl=True,
    )
    print(player.__dict__)
    print(repr(player))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
