# -*- coding: utf-8 -*-

"""Module for write locks to do with databases.  When this is no longer used, we're ready for multiprocess database writes"""

import threading
import logging
import time
from j5.OS import ThreadRaise
from j5.OS import ThreadDebug
from j5.Logging import Errors

database_write_lock = threading.Condition()
# This is a dictionary in case it is worth it to implement more fine-grained locks
# So the lock at None is the whole database lock, whereas if we implemented table locks
# they would use the table name as a key
thread_busy = {}
MAX_LOCK_WAIT_TIMEOUT = 120
LOCK_WARNING_TIMEOUT = 30

def no_database_writes(f):
    f.does_database_writes = False
    return f

def get_db_lock(max_wait_for_exclusive_lock=MAX_LOCK_WAIT_TIMEOUT, warning_timeout=LOCK_WARNING_TIMEOUT):
    timeout_warned = None
    with (database_write_lock):
        current_id = ThreadRaise.get_thread_id(threading.currentThread())
        busy_op = thread_busy.get(None, None)
        if busy_op and busy_op[0] == current_id:
            # Multi-entrant
            thread_busy[None][2] += 1
            return
        # This is used to measure the max time for timeout purposes
        start_time = time.time()
        # This is used to make sure we don't wait too long on the notify
        check_start_time = start_time
        while busy_op:
            logging.info('Thread %s waiting for Thread %s to release database lock (maximum wait %ds)',
                current_id, busy_op[0], max_wait_for_exclusive_lock)
            database_write_lock.wait(warning_timeout - (time.time() - check_start_time))
            now_busy_op = thread_busy.get(None, None)
            # Make sure we've waited the timeout time, as the same thread can release and catch the lock multiple times
            if now_busy_op and busy_op[:2] == now_busy_op[:2]:
                if (time.time() - start_time > max_wait_for_exclusive_lock): #same op is still busy
                    # Time to kill this
                    frame = ThreadDebug.find_thread_frame(busy_op[0])
                    last_trace_back = ThreadDebug.format_traceback(frame)
                    logging.error('Thread %s timed out waiting for Thread %s to release database lock ... Killing blocking thread ...',
                        current_id, busy_op[0])
                    logging.info("Traceback of thread to be killed:\n%s",last_trace_back)
                    try:
                        ThreadRaise.thread_async_raise(busy_op[0], RuntimeError)
                    except Exception as e:
                        logging.error("Could not raise exception in thread %s - %e", busy_op[0], e)
                        logging.info(Errors.traceback_str())
                    busy_op = None
                elif (time.time() - check_start_time > warning_timeout) and timeout_warned != busy_op[:2]:
                    # Warn of implending timeout
                    frame = ThreadDebug.find_thread_frame(busy_op[0])
                    last_trace_back = ThreadDebug.format_traceback(frame)
                    logging.warning("Thread %s still waiting for database lock after %ds - this may timeout", current_id, warning_timeout)
                    logging.info(last_trace_back)
                    timeout_warned = busy_op[:2]
            else:
                busy_op = now_busy_op
                check_start_time = time.time()

        thread_busy[None] = [current_id, time.time(), 1]

def release_db_lock():
    with (database_write_lock):
        current_id = ThreadRaise.get_thread_id(threading.currentThread())
        busy_op = thread_busy.get(None, None)
        if busy_op and busy_op[0] == current_id:
            busy_op[2] -= 1
            if busy_op[2] <= 0:
                thread_busy.pop(None, None)
                database_write_lock.notify()

