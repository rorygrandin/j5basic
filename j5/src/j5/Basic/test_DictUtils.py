
import Namespace
from Basic import DictUtils

def test_cikeys():
    d = DictUtils.cidict()
    d["VaLuE"] = 5
    assert d["value"] == 5
    
