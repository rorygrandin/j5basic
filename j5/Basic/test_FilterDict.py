from j5.Basic import DictUtils
from j5.Basic import FilterDict

def test_filterdict_to_str_etc():
    filter1 = {"test": ["me"]}
    filter1_str = FilterDict.filterdict_to_str(filter1)
    filter1_dict = FilterDict.str_to_filterdict(filter1_str)
    assert filter1_dict == filter1
    assert isinstance(filter1_dict, FilterDict.filterdict)
    filter2 = {"test": ["me","you"], "exempt": ["everyone","else"], "ignore": []}
    filter2_str = FilterDict.filterdict_to_str(filter2)
    filter2_dict = FilterDict.str_to_filterdict(filter2_str)
    assert filter2_dict == filter2
    assert isinstance(filter2_dict, FilterDict.filterdict)

def test_filterdict_to_str_unicode():
    filter1 = {u"test\u3a42": [u"me\u1a23"]}
    filter1_str = FilterDict.filterdict_to_str(filter1)
    filter1_dict = FilterDict.str_to_filterdict(filter1_str)
    assert filter1_dict == filter1
    assert isinstance(filter1_dict, FilterDict.filterdict)
    filter2 = {u"test\u3a42": [u"me\u1a23","you"], "exempt": ["everyone","else"], "ignore": []}
    filter2_str = FilterDict.filterdict_to_str(filter2)
    filter2_dict = FilterDict.str_to_filterdict(filter2_str)
    assert filter2_dict == filter2
    assert isinstance(filter2_dict, FilterDict.filterdict)

def test_filterdict_combine():
    filter1 = {'this': 3, 'is': 4}
    filter2 = {'is': 5,'combined': 6}
    combined = FilterDict.combine_filterdicts(filter1, filter2)
    DictUtils.assert_dicts_equal(filter1, {'this': 3, 'is': 4})
    DictUtils.assert_dicts_equal(filter2, {'is': 5, 'combined': 6})
    DictUtils.assert_dicts_equal(combined, {'this': [3], 'is': [4,5], 'combined': [6]})
    assert isinstance(combined, FilterDict.filterdict)

def test_empty_filter_is_not_blank():
    assert FilterDict.filterdict_to_str({}) != ""
    assert FilterDict.str_to_filterdict(FilterDict.filterdict_to_str({})) == {}
    assert isinstance(FilterDict.str_to_filterdict(FilterDict.filterdict_to_str({})), FilterDict.filterdict)
    assert FilterDict.str_to_filterdict("") is None
    assert FilterDict.filterdict_to_str(None) == ""
