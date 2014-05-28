from j5basic import TimeCache
from j5test.Utils import raises
import datetime
import time

class TestTimeCache(object):
    def test_basic(self):
        d = TimeCache.timecache(0.01)
        d[1] = "test"
        assert 1 in d
        assert d[1] == "test"
        time.sleep(0.02)
        d.purge()
        assert not d

    def test_call_cleanup(self):
        cleanups_called = []
        class cleany(TimeCache.timecache):
            def cleanup_key(self, key, value):
                cleanups_called.append((dict.__contains__(self, key), key, value))
        # a cunning trick to make sure values are always expired immediately, thus speeding the test
        d = cleany(-1)
        d[1] = "test"
        d.purge()
        # check that the cleanup was called after the removal (hence False), with the correct values
        assert cleanups_called == [(False, 1, "test")]

    @classmethod
    def setUp(cls):
        cls.orig_global_disabled = TimeCache.GLOBAL_CACHE_DISABLED
        cls.orig_local_disabled = TimeCache.LOCAL_CACHE_DISABLED

    @classmethod
    def tearDown(cls):
        TimeCache.GLOBAL_CACHE_DISABLED = cls.orig_global_disabled
        TimeCache.LOCAL_CACHE_DISABLED = cls.orig_local_disabled

    @classmethod
    def setup_method(cls, method):  # This is a wrapper of setUp for py.test (py.test and nose take different method setup methods)
        cls.setUp()

    @classmethod
    def teardown_method(cls, method):  # This is a wrapper of tearDown for py.test (py.test and nose take different method setup methods)
        cls.tearDown()

    def test_global_disable(self):
        d = TimeCache.timecache(10)
        d[1] = "test"
        assert 1 in d
        TimeCache.GLOBAL_CACHE_DISABLED = True
        assert 1 not in d
        d[2] = "missing"
        assert not d.items()
        TimeCache.GLOBAL_CACHE_DISABLED = False
        assert d[1] == "test"
        assert 2 not in d

    def test_local_disable(self):
        d = TimeCache.timecache(10)
        e = TimeCache.timecache(10)
        d.LOCAL_CACHE = True
        d[1] = "test"
        e[1] = "test"
        assert 1 in d
        assert 1 in e
        TimeCache.LOCAL_CACHE_DISABLED = True
        assert 1 not in d
        assert 1 in e
        d[2] = "missing"
        e[2] = "missing"
        assert not d.items()
        assert sorted(e.items()) == [(1, "test"), (2, "missing")]
        TimeCache.LOCAL_CACHE_DISABLED = False
        assert d[1] == "test"
        assert 2 not in d
        assert sorted(e.items()) == [(1, "test"), (2, "missing")]

    def test_local_timelimit(self):
        d = TimeCache.timecache(10, True)
        e = TimeCache.timecache(10)
        assert d.LOCAL_CACHE == True
        d[1] = "test"
        e[1] = "test"
        assert 1 in d
        assert 1 in e
        TimeCache.LOCAL_CACHE_TIMELIMIT = datetime.timedelta(seconds=0.1)
        time.sleep(0.2)
        assert 1 not in d
        assert 1 in e
        d[2] = "missing"
        e[2] = "missing"
        assert d.items() == [(2, "missing")]
        assert sorted(e.items()) == [(1, "test"), (2, "missing")]
        TimeCache.LOCAL_CACHE_TIMELIMIT = None
        time.sleep(0.2)
        assert 1 not in d
        assert d[2] == "missing"
        assert sorted(e.items()) == [(1, "test"), (2, "missing")]

    def test_purge_on_set (self):
        d = TimeCache.timecache(1)
        d[0] = datetime.datetime.now()
        d[1] = datetime.datetime.now()
        assert len(d) == 2
        time.sleep(2)
        assert len(d) == 2
        d[2] = datetime.datetime.now()
        assert len(d) == 1
        time.sleep(1)
        d[3] = datetime.datetime.now()
        time.sleep(1)
        d[4] = datetime.datetime.now()
        assert len(d) == 1

