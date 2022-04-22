# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

from .exceptions import BaseException
from collections import UserDict


class DataRecord(UserDict):
    class InvalidDataError(BaseException):
        pass

    class ReadOnlyError(BaseException):
        pass

    def __init__(self, **kwargs):

        super().__setattr__("data", {})
        super().__setattr__("_DataRecord__sealed", False)
        super().__init__(self, **kwargs)
        super().__setattr__("_DataRecord__sealed", True)

        for key in kwargs:
            if key in self.__dict__:
                raise DataRecord.InvalidDataError(
                    f"'{key}' is a reserved field name of "
                    f"{self.__class__.__name__}"
                )

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        if self.__sealed:
            raise DataRecord.ReadOnlyError(
                f"DataRecord is read-only, cannot assign {key}={value}"
            )
        else:
            super().__setitem__(key.lower(), value)

    def __delitem__(self, key):
        raise DataRecord.ReadOnlyError(
            f"DataRecord is read-only, cannot delete {key}"
        )

    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr.lower())
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' has no attribute '{attr}'"
            )

    def __setattr__(self, attr, value):
        if self.__dict__.get("_DataRecord__sealed", False):
            raise DataRecord.ReadOnlyError(
                f"DataRecord is read-only, cannot assign {attr}={value}"
            )
        else:
            super().__setattr__(attr.lower(), value)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.data})>"


class Placeholder(DataRecord):
    def __init__(self, name, **kwargs):
        self.__name = name
        super().__init__(name=name, **kwargs)

    def set(self, obj):
        self.__dict__["_DataRecord__sealed"] = False
        self.__class__ = obj.__class__
        self.__dict__ = obj.__dict__

    def __bool__(self):
        return False

    def __str__(self):
        return getattr(self, f"_{self.__class__.__name__}__name", self.name)


if __name__ == "__main__":
    d = DataRecord(one=1, two=2, three=3)
    print(vars(d))
    print(repr(d))
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        pass
