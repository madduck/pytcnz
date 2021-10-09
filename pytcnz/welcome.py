#!/usr/bin/python3
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from .meta import email, author

if __name__ == '__main__':
    print(f"""


Congratulations, you've successfully installed pytcnz
Drop me a line at {email} and tell me how you fare!

Have fun! -{author.split()[0]}







(this is file {__file__})")
""")
