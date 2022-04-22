# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from .exceptions import BaseException
import phonenumbers


class PhoneNumber:
    class InvalidPhoneNumber(BaseException):
        pass

    @classmethod
    def fixup(cls, numberstr, region):
        return numberstr
        cc = phonenumbers.country_code_for_region(region)
        if not numberstr.startswith("0") and not numberstr.startswith(str(cc)):
            return f"0{numberstr}"

    def __init__(self, numberstr, region="NZ", mobileprefixes=("02",)):
        self.__raw = numberstr
        self.__mobileprefixes = mobileprefixes
        numberstr = PhoneNumber.fixup(numberstr, region)
        try:
            self.__number = phonenumbers.parse(numberstr, region)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise PhoneNumber.InvalidPhoneNumber(numberstr)

        if not phonenumbers.is_valid_number_for_region(self.__number, region):
            raise PhoneNumber.InvalidPhoneNumber(numberstr)

    def __str__(self):
        trans = str.maketrans("", "", "-/ ")
        return phonenumbers.format_number(
            self.__number, phonenumbers.PhoneNumberFormat.NATIONAL
        ).translate(trans)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self} from {self.__raw})>"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return str(self).__hash__()

    def is_mobile_number(self):
        for pfx in self.__mobileprefixes:
            if str(self).startswith(pfx):
                return True
        return False


if __name__ == "__main__":
    nr = PhoneNumber("64/021/1100938")
    print(vars(nr))
    print(repr(nr))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
