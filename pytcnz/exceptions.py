# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

_PyBaseException = BaseException


class BaseException(_PyBaseException):
    pass


class InvalidDataError(BaseException):
    pass
