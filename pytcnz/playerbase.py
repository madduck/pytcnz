# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from .exceptions import BaseException
from .gender import Gender
from .datarecord import DataRecord


class PlayerBase(DataRecord):
    class BaseException(BaseException):
        pass

    class UnknownFieldError(BaseException):
        pass

    def __init__(self, *, name, gender, **kwargs):
        gender = Gender.from_string(gender)
        super().__init__(name=name, gender=gender, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name} ({self.gender}))>"

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.name.__lt__(other.name)

    def __hash__(self):
        hash(self.name)

    def fill_template(self, template, **extra_data):
        d = self.data | extra_data
        tried_lowercase = False
        while True:
            try:
                return template.format(**d)

            except KeyError as e:
                if not tried_lowercase:
                    arg = e.args[0]
                    argl = arg.lower()
                    d[arg] = d[argl]
                    tried_lowercase = True
                    continue

                raise PlayerBase.UnknownFieldError(
                    f"Field {argl} is not one of "
                    f"{', '.join(sorted(d.keys()))}"
                )


if __name__ == "__main__":
    player = PlayerBase(name="Martin Krafft", gender="M")
    print(vars(player))
    print(repr(player))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
