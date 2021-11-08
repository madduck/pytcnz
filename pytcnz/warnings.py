# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys


class Warning:
    def __init__(self, details, *, context=None, **kwargs):
        self.__details = details
        self.__context = context
        self.__additional = kwargs

    details = property(lambda s: s.__details)
    context = property(lambda s: s.__context)
    additional = property(lambda s: s.__additional)

    def __str__(self):
        r = (
            f"While {self.__context[0].lower()}{self.__context[1:]}: "
            if self.__context
            else ""
        )
        r = f"{r}{self.__details}"
        if self.__additional:
            r = f"{r} ({additional})"
        return r

    def __repr__(self):
        return f'<{self.__class__.__name__}("{self.__details}")>'

    def __eq__(self, other):
        return (
            self.__details == other.__details
            and self.__context == other.__context
            and self.__additional == other.__additional
        )


class _Warnings(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.warnings = []
        return cls._instance

    def __iter__(self):
        return self.__class__._instance.warnings.__iter__()

    def __len__(self):
        return self.__class__._instance.warnings.__len__()

    def __getitem__(self, item):
        return self.__class__._instance.warnings.__getitem__(item)

    def __eq__(self, other):
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__}({len(self)} entries)>"

    def __del__(self):
        if self.__class__._instance.warnings:
            print("Warnings:", file=sys.stderr)
            print(self.get_string(indent=" "), file=sys.stderr)

    def add(self, details, *, skip_duplicates=True, context=None, **kwargs):
        w = Warning(details=details, context=context, **kwargs)
        if not skip_duplicates or w not in self.__class__._instance.warnings:
            self.__class__._instance.warnings.append(w)

    def clear(self):
        self.__class__._instance.warnings = []

    def get_string(self, *, separator="\n", indent=None):
        indent = indent or ""
        return separator.join(map(lambda s: f"{indent}{s!s}", self))

    def print_all(
        self,
        *,
        file=sys.stderr,
        separator="\n",
        indent=None,
        before=None,
        after=None,
    ):
        if before:
            print(before, file=file)
        print(self.get_string(separator=separator, indent=indent), file=file)
        if after:
            print(after, file=file)


Warnings = _Warnings()
