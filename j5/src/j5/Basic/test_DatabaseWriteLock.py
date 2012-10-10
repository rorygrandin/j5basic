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
from j5.Basic.DatabaseWriteLock import DatabaseLockTooLong
from j5.Logging import Errors
from j5.OS import ThreadRaise, ThreadDebug

# TODO: Test multi-entrant locking explicitly

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

class ExceptionHandlingThread(threading.Thread):
    def __init__(self, target=None, **kwargs):
        super(ExceptionHandlingThread, self).__init__(target=self.safe_run, **kwargs)
        self.actual_target = target
        self.exception = None
        self.timeout_exception = None

    def safe_run(self, *args, **kwargs):
        try:
            self.actual_target(*args, **kwargs)
        except DatabaseLockTooLong, dbex:
            logging.info("%r:\n%s", self, Errors.traceback_str())
            self.timeout_exception = dbex
        except Exception, ex:
            logging.info("%r:\n%s", self, Errors.traceback_str())
            self.exception = ex

    @classmethod
    def join_threads(cls, *threads, **kwargs):
        timeout = kwargs.get('timeout', 20)
        use_join = kwargs.get('use_join', True)
        deadlock=False
        for thread in threads:
            if thread.exception is not None:
                logging.error("Thread %s died with %r", thread.exception, thread)
        for thread in threads:
            if use_join:
                #Join has some problems with the DatabaseTooLongError
                thread.join(timeout)
            else:
                for t in range(timeout):
                    if thread.isAlive():
                        time.sleep(1)

            if thread.isAlive():
                deadlock = True
                break

        if deadlock:
            for thread in threads:
                if thread.isAlive():
                    thread_id = ThreadRaise.get_thread_id(thread)
                    frame = ThreadDebug.find_thread_frame(thread_id)
                    last_trace_back = "\n".join(ThreadDebug.format_traceback(frame))
                    logging.error("Stuck thread: %r\n:%s", thread, last_trace_back)
            raise AssertionError("Threads are still alive")

        for thread in threads:
            assert thread.exception is None, "'%r' in launched thread" % thread.exception


#I don't understand what this is testing ...
class TestParallelWriteLockAccess(object):
    def do_something(self, name, total):
        DatabaseWriteLock.get_db_lock()
        try:
            read = total[0]
            total[0] = read + 1
        finally:
            DatabaseWriteLock.release_db_lock()

    def test_parallel_access(self):
        for j in range(10):
            class server:
                mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
            DatabaseWriteLock.ServerMode().server = server
            assert not DatabaseWriteLock.database_lock_queue
            num_threads = 30
            total = [0]
            threads = []
            expected_names = set()
            for i in range(num_threads):
                name = "Lock-%d" % i
                expected_names.add(name)
                threads.append(ExceptionHandlingThread(target=self.do_something, args=(name,total), name=name))
            for thread in threads:
                thread.start()

            ExceptionHandlingThread.join_threads(*threads)

            assert total[0] == num_threads, 'Expected %d, got %d' % (num_threads, total[0])
            assert not DatabaseWriteLock.database_lock_queue

class TestWarningTimeout(object):
    def do_something_for_a_little_too_long(self):
        DatabaseWriteLock.get_db_lock(warning_timeout=2)
        try:
            time.sleep(3)
        finally:
            DatabaseWriteLock.release_db_lock()

    def do_something_else(self):
        DatabaseWriteLock.get_db_lock(warning_timeout=2)
        try:
            time.sleep(0.1)
        finally:
            DatabaseWriteLock.release_db_lock()

    def test_warning_timeout(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
        DatabaseWriteLock.ServerMode().server = server
        first_thread = ExceptionHandlingThread(target=self.do_something_for_a_little_too_long, name="first_thread")
        second_thread = ExceptionHandlingThread(target=self.do_something_else, name="second_thread")
        first_thread.start()
        second_thread.start()
        second_thread_str = str(second_thread)
        ExceptionHandlingThread.join_threads(first_thread, second_thread)

        assert ("Thread %s still waiting for database lock after 2s - this may timeout" % second_thread_str) in DatabaseWriteLock.logging._warning

    def test_only_one_warning(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
        DatabaseWriteLock.ServerMode().server = server
        first_thread = ExceptionHandlingThread(target=self.do_something_for_a_little_too_long, name="first_thread")
        second_threads = [ExceptionHandlingThread(target=self.do_something_else, name="other_thread-%d" % i) for i in range(3)]
        first_thread.start()
        # Make sure the first thread gets the lock first
        time.sleep(0.5)
        for second_thread in second_threads:
            second_thread.start()
        ExceptionHandlingThread.join_threads(first_thread, *second_threads)
        assert len(DatabaseWriteLock.logging._warning) == 1
        assert "still waiting for database lock after 2s - this may timeout" in DatabaseWriteLock.logging._warning[0]


class TestMaxWaitTimeout(object):
    def do_something_for_awhile(self, name):
        with ThreadWeave.only_thread_blocking('first_thread') as StatementSkipped.detector:
            # Make sure the first thread gets the lock first
            DatabaseWriteLock.get_db_lock(2)
        with ThreadWeave.only_thread('second_thread') as StatementSkipped.detector:
            # Then the second thread tries to get the lock
            DatabaseWriteLock.get_db_lock(2, 1)
        try:
            with ThreadWeave.only_thread('first_thread') as StatementSkipped.detector:
                # First thread holds on for too long
                for i in range(4):
                    time.sleep(1)
            with self.run_lock:
                self.run.add(name)
        finally:
            DatabaseWriteLock.release_db_lock()

    def test_max_wait_timeout(self):
        for i in range(10):
            DatabaseWriteLock.logging.clear()
            class server:
                mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
            DatabaseWriteLock.ServerMode().server = server
            self.run_lock = threading.Lock()
            self.run = set()
            first_thread = ExceptionHandlingThread(target=self.do_something_for_awhile, args=("first_thread",), name="first_thread")
            second_thread = ExceptionHandlingThread(target=self.do_something_for_awhile, args=("second_thread",), name="second_thread")
            first_thread.start()
            second_thread.start()
            ExceptionHandlingThread.join_threads(first_thread, second_thread, use_join=False)
            assert "second_thread" in self.run
            assert len(DatabaseWriteLock.logging._error) >= 1
            error_log = DatabaseWriteLock.logging._error[0]
            assert " timed out waiting for Thread " in error_log
            assert " to release database lock ... Killing blocking thread ..." in error_log

class TestCompetingTimeouts(object):
    def do_something_for_awhile(self, name):
        with ThreadWeave.only_thread_blocking('first_thread') as StatementSkipped.detector:
            # Make sure the first thread gets the lock first
            DatabaseWriteLock.get_db_lock(2)
        # Then they all try to get the lock - this will be reentrant on first_thread
        DatabaseWriteLock.get_db_lock(2, 1)
        try:
            with ThreadWeave.only_thread('first_thread') as StatementSkipped.detector:
                # First thread holds on for too long
                for i in range(4):
                    time.sleep(1)
            with ThreadWeave.only_thread('second_thread') as StatementSkipped.detector:
                # Wait long enough for third thread to try to kill us unless it correctly resets its timeout
                time.sleep(0.8)
            with self.run_lock:
                self.run.add(name)
        finally:
            DatabaseWriteLock.release_db_lock()
            with ThreadWeave.only_thread('first_thread') as StatementSkipped.detector:
                # We took the lock twice - release it again
                DatabaseWriteLock.release_db_lock()

    def test_competing_timeout(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
        DatabaseWriteLock.ServerMode().server = server
        self.run_lock = threading.Lock()
        self.run = set()
        first_thread = ExceptionHandlingThread(target=self.do_something_for_awhile, args=("first_thread",), name="first_thread")
        second_thread = ExceptionHandlingThread(target=self.do_something_for_awhile, args=("second_thread",), name="second_thread")
        third_thread = ExceptionHandlingThread(target=self.do_something_for_awhile, args=("third_thread",), name="third_thread")
        first_thread.start()
        second_thread.start()
        third_thread.start()
        ExceptionHandlingThread.join_threads(first_thread, second_thread, third_thread, use_join=False)
        assert "second_thread" in self.run
        assert "third_thread" in self.run

class TestJoiningQueueNothingBusy(object):
    def run_lock_clear_test(self):
        with ThreadWeave.only_thread('first_thread') as StatementSkipped.detector:
            DatabaseWriteLock.get_db_lock(2,1)
            try:
                with self.run_lock:
                    self.run.add("first_thread")
            finally:
                DatabaseWriteLock.release_db_lock()
        with ThreadWeave.only_thread('second_thread') as StatementSkipped.detector:
            with (DatabaseWriteLock.database_write_lock):
                DatabaseWriteLock.database_lock_queue.remove("TEST")
                DatabaseWriteLock.database_write_lock.notifyAll()

    def ctest_joining_queue_when_nothing_busy(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SINGLE
        DatabaseWriteLock.ServerMode().server = server
        with (DatabaseWriteLock.database_write_lock):
            DatabaseWriteLock.database_lock_queue.append("TEST")
        self.run_lock = threading.Lock()
        self.run = set()
        first_thread = ExceptionHandlingThread(target=self.run_lock_clear_test, name="first_thread")
        second_thread = ExceptionHandlingThread(target=self.run_lock_clear_test, name="second_thread")
        first_thread.start()
        second_thread.start()
        ExceptionHandlingThread.join_threads(first_thread, second_thread)
        assert "first_thread" in self.run

class TestSlaveError(object):
    def test_slave_error(self):
        DatabaseWriteLock.logging.clear()
        class server:
            mode = DatabaseWriteLock.Admin.ServerModeEnum.SLAVE
        DatabaseWriteLock.ServerMode().server = server
        DatabaseWriteLock.get_db_lock()
        DatabaseWriteLock.release_db_lock()
        assert "Requesting DatabaseWriteLock on SLAVE process.  Traceback in info logs" in DatabaseWriteLock.logging._error

