#!/usr/bin/env python

from j5.Basic import EnumClass
from j5.Test import Utils

class MyEnum(EnumClass.enum):
    APPLES = 1
    ORANGES = 2

class TestEnum(object):
    """Tests creating and using EnumClass.enum objects"""
    def test_create(self):
        """Tests the creation of enums, and that values can be looked up"""
        assert MyEnum.APPLES == 1
        assert MyEnum.ORANGES == 2
        assert MyEnum.get_name() == "MyEnum"

    def test_identify(self):
        """Tests finding the names mapped to constants (and failure to find)"""
        assert MyEnum.identify(1) == "APPLES"
        assert MyEnum.identify(2) == "ORANGES"
        assert Utils.raises(KeyError, MyEnum.identify, 3)
        assert MyEnum.identify(3, "MONKEY") == "MONKEY"

    def test_lookup(self):
        """Tests looking up an enum by name"""
        assert MyEnum.lookup("APPLES") == 1
        assert MyEnum.lookup("ORANGES") == 2
        assert Utils.raises(KeyError, MyEnum.lookup, "PEARS")
        assert MyEnum.lookup("PEARS", 4) == 4

    def test_iter(self):
        """Tests that you can iterate over constants"""
        assert list(iter(MyEnum)) == [1, 2]

