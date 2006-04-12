
import Namespace
from Basic import DictUtils

class TestCIDict:
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

class TestAttrDict:
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

