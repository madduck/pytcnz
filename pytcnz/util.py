# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys
import os.path
from datetime import datetime
from pytz import timezone as tz


def get_timestamp(*, timezone="Pacific/Auckland", fmt="%F %T %Z", moment=None):
    if moment is None:
        moment = datetime.now(tz=tz(timezone))
    return moment.strftime(fmt)


def get_config_filename():
    filepath = os.path.realpath(sys.argv[0])
    basedir = os.path.realpath(os.path.join(os.path.dirname(filepath), ".."))
    return os.path.join(basedir, "tctools.ini")
