# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from datetime import datetime
from pytz import timezone as tz


def get_timestamp(*, timezone="Pacific/Auckland", fmt="%F %T %Z", moment=None):
    if moment is None:
        moment = datetime.now(tz=tz(timezone))
    return moment.strftime(fmt)
