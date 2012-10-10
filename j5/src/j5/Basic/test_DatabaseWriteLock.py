# -*- coding: utf-8 -*-
"""Test module for DatabaseWriteLock"""

"""
Scenarios to test:
    * Parallel threads do not threadlock
    * Locking a thread for warning_timeout when someone else wants it causes a warning to be logged
    * Locking a thread for max_wait_for_exclusive_lock causes an attempt at killing the offending thread
    * When a thread has the lock and two others go for it, and it stalls long enough to timeout, only one thread triggers the killing, and the second thread does not kill the one which has just done the killing
"""

import threading
import time
from j5.Test import ThreadWeave
from j5.Basic.WithContextSkip import StatementSkipped
from j5.Basic import DatabaseWriteLock

class TestParallelWriteLockAccess(object):
    def do_something(self, name):
        DatabaseWriteLock.get_db_lock()
        try:
            with self.run_lock:
                self.run.add(name)
            time.sleep(0.05)
        finally:
            DatabaseWriteLock.release_db_lock()

    def test_parallel_access(self):
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
        DatabaseWriteLock.ServerMode().server = server
        self.run_lock = threading.Lock()
        self.run = set()
        threads = []
        expected_names = set()
        for i in range(10):
            name = "Lock-%d" % i
            expected_names.add(name)
            threads.append(threading.Thread(target=self.do_something, args=(name,), name=name))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert expected_names == self.run

