# -*- coding: utf-8 -*-
"""Test module for DatabaseWriteLock"""

"""
Scenarios to test:
    * Parallel threads do not threadlock
    * Locking a thread for warning_timeout when someone else wants it causes a warning to be logged
    * Locking a thread for max_wait_for_exclusive_lock causes an attempt at killing the offending thread
    * When a thread has the lock and two others go for it, and it stalls long enough to timeout, only one thread triggers the killing, and the second thread does not kill the one which has just done the killing
    * Trying to get the lock while a SLAVE causes an error to be logged (but proceeds)
"""

import threading
import time
import logging
from j5.Test import ThreadWeave
from j5.Basic.WithContextSkip import StatementSkipped
from j5.Basic import DatabaseWriteLock

class instrumented_logging(object):
    def __init__(self):
        self._loglock = threading.Lock()
        self.clear()

    def error(self, msg, *args):
        with self._loglock:
            self._error.append(msg % args)
        logging.error(msg, *args)

    def warning(self, msg, *args):
        with self._loglock:
            self._warning.append(msg % args)
        logging.warning(msg, *args)

    def info(self, msg, *args):
        with self._loglock:
            self._info.append(msg % args)
        logging.info(msg, *args)

    def clear(self):
        with self._loglock:
            self._error = []
            self._info = []
            self._warning = []

# Override logging module
DatabaseWriteLock.logging = instrumented_logging()

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

class TestWarningTimeout(object):
    def do_something_for_awhile(self):
        with ThreadWeave.only_thread('second_thread') as StatementSkipped.detector:
            # Make sure the first thread gets the lock first
            time.sleep(0.5)
        DatabaseWriteLock.get_db_lock(warning_timeout=2)
        try:
            with ThreadWeave.only_thread('first_thread') as StatementSkipped.detector:
                time.sleep(3)
        finally:
            DatabaseWriteLock.release_db_lock()

    def test_warning_timeout(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
        DatabaseWriteLock.ServerMode().server = server
        first_thread = threading.Thread(target=self.do_something_for_awhile, name="first_thread")
        second_thread = threading.Thread(target=self.do_something_for_awhile, name="second_thread")
        first_thread.start()
        second_thread.start()
        first_thread.join()
        second_thread.join()
        assert ("Thread %s still waiting for database lock after 2s - this may timeout" % second_thread.ident) in DatabaseWriteLock.logging._warning

class TestSlaveError(object):
    def test_slave_error(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SLAVE
        DatabaseWriteLock.ServerMode().server = server
        DatabaseWriteLock.get_db_lock()
        DatabaseWriteLock.release_db_lock()
        assert "Requesting DatabaseWriteLock on SLAVE process.  Traceback in info logs" in DatabaseWriteLock.logging._error

