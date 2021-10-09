# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from .datarecord import DataRecord
from .gender import Gender
from .exceptions import BaseException


class Draw(DataRecord):
    class InvalidDataError(BaseException):
        pass

    def __init__(self, name, *, gendered=None, **kwargs):
        if gendered is not None:
            gendered = Gender.from_string(gendered)

        super().__init__(name=name, gendered=gendered, **kwargs)

    def __repr__(self):
        s = f"<{self.__class__.__name__}({self.name}"
        try:
            s = f"{s}, {self.description}"
        except AttributeError:
            pass
        return f"{s})>"

    def __str__(self):
        return self.name

    def __lt__(self, other):
        if self.get("ladies_first", True) and other.get("ladies_first", True):

            def women_first(name):
                return name.replace("W", "0").replace("M", "1")

            return women_first(self.name).__lt__(women_first(other.name))
        else:
            return self.name.__lt__(other.name)

    def __hash__(self):
        return hash(self.name)


if __name__ == "__main__":
    draw = Draw("W0", description="Women's Open", gendered=Gender.N)
    print(vars(draw))
    print(repr(draw))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
