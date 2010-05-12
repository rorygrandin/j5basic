from j5.Basic import TimeCache
from j5.Test.Utils import raises
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
    def setup_method(self, method):
        self.orig_disabled = TimeCache.GLOBAL_CACHE_DISABLED

    @classmethod
    def teardown_method(self, method):
        TimeCache.GLOBAL_CACHE_DISABLED = self.orig_disabled

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
