
from j5basic import DictUtils
from j5test.Utils import raises

class TestUniqueItems(object):
    def test_unique_items(self):
        l = [9, 3, 4, 2, 4, 5, 3, 9]
        assert list(DictUtils.unique_items(l)) == [9, 3, 4, 2, 5]

class TestCIDict(object):
    def test_get(self):
        d = DictUtils.cidict()
        d["VaLuE"] = 5
        assert d["value"] == 5

    def test_retaincase(self):
        """tests that the key's original case is retained"""
        d = DictUtils.cidict()
        d["VaLuE"] = 5
        assert "VaLuE" in d.keys()
        assert "value" not in d.keys()

class TestAttrDict(object):
    def test_attrs(self):
        d = DictUtils.attrdict()
        d["VaLuE"] = 5
        assert d["VaLuE"] == 5
        assert d.VaLuE == 5

    def test_attribify(self):
        nested = DictUtils.attribify([{"this": "is", "a": ["nested", {"dictionary": 4}]}])
        assert nested[0].this == "is"
        assert nested[0].a[0] == "nested"
        assert nested[0].a[1].dictionary == 4

    def test_missing_attr(self):
        d = DictUtils.attrdict()
        d["VaLuE"] = 5
        assert "HeGeMoNy" not in d.keys()
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy", 9) == 9
        assert raises(AttributeError, getattr, d, "HeGeMoNy")

    def test_default_attr(self):
        d = DictUtils.attrdict()
        d["VaLuE"] = 5
        d.set_default_value(32)
        assert "HeGeMoNy" not in d.keys()
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy") == 32
        assert getattr(d, "HeGeMoNy", 9) == 32

class TestSetAttrDict(object):
    def test_set_attrs(self):
        """tests setting attributes both dict- and object-style"""
        d = DictUtils.setattrdict()
        d["VaLuE"] = 5
        assert d["VaLuE"] == 5
        assert d.VaLuE == 5
        d.ReDeeM = "price"
        assert d["ReDeeM"] == "price"
        assert d.ReDeeM == "price"

    def test_missing_attr(self):
        d = DictUtils.setattrdict()
        d.VaLuE = 5
        assert "HeGeMoNy" not in d.keys()
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy", 9) == 9
        assert raises(AttributeError, getattr, d, "HeGeMoNy")

    def test_default_attr(self):
        d = DictUtils.attrdict()
        d.VaLuE = 5
        d.set_default_value(32)
        assert "HeGeMoNy" not in d.keys()
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy") == 32
        assert getattr(d, "HeGeMoNy", 9) == 32

class TestOrderedDict(object):
    def test_key_and_value_ordering(self):
        k = [5,1,2,3,7,6]
        v = ["a","b","c","d","e","f"]
        d = DictUtils.ordereddict(zip(k,v))

        assert d.keys() == k
        assert d.values() == v
        assert d.items() == zip(k,v)
        assert list(d.iterkeys()) == k
        assert list(d.itervalues()) == v
        assert list(d.iteritems()) == zip(k,v)

    def test_setting(self):
        k = [5,1,2,3,7,6]
        v = ["a","b","c","d","e","f"]
        d = DictUtils.ordereddict(zip(k,v))
        d.setdefault(8,"g")
        k.append(8)
        v.append("g")

        assert d.keys() == k
        assert d.values() == v
        assert d.items() == zip(k,v)
        assert list(d.iterkeys()) == k
        assert list(d.itervalues()) == v
        assert list(d.iteritems()) == zip(k,v)

class TestDictHelpers(object):
    def test_assert_dicts_equal(self):
        d1 = {1:2, 3:4}
        d2 = {1:2, 3:4}
        d3 = {1:3, 3:5}
        d4 = {2:1, 4:3}

        DictUtils.assert_dicts_equal(d1, d2)
        DictUtils.assert_dicts_not_equal(d1, d3)
        DictUtils.assert_dicts_not_equal(d1, d4)


