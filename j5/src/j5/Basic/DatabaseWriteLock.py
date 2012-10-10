# -*- coding: utf-8 -*-

"""Module for write locks to do with databases.  When this is no longer used, we're ready for multiprocess database writes"""

import threading
import logging
import time
from j5.OS import ThreadRaise
from j5.OS import ThreadDebug
from j5.Logging import Errors
from j5.Control.Interface import Notification
from j5.Control import Ratings
from j5.Text.Conversion import wiki2html

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
                    traceback_lines = ["=== Tracebacks from attempt to kill blocking thread==="]
                    frame = ThreadDebug.find_thread_frame(busy_op[0])
                    last_trace_back = ThreadDebug.format_traceback(frame)
                    logging.error('Thread %s timed out waiting for Thread %s to release database lock ... Killing blocking thread ...',
                        current_id, busy_op[0])
                    logging.info("Traceback of thread to be killed:\n%s","\n".join(last_trace_back))
                    try:
                        ThreadRaise.thread_async_raise(busy_op[0], RuntimeError)
                        traceback_lines.append("== RuntimeError raised in Thread %s ==" % busy_op[0])
                    except Exception as e:
                        msg = "Could not raise exception in thread %s - %e" % (busy_op[0], e)
                        logging.error(msg)
                        traceback_lines.append("== %s ==" % msg)
                        tb = Errors.traceback_str()
                        logging.info(tb)
                        traceback_lines.append("{{{")
                        traceback_lines.extend(tb.split("\n"))
                        traceback_lines.append("}}}")
                    traceback_lines.append("== Traceback of killed thread %s ==" % busy_op[0])
                    traceback_lines.append("{{{")
                    traceback_lines.extend(last_trace_back)
                    traceback_lines.append("}}}")
                    dump_file_contents = wiki2html.creole2xhtml("\n".join(traceback_lines))
                    email_msg = "\n".join([
                        "== Blocking Thread in Database Lock ==",
                        "The thread %s has blocked the Database Lock for over %ds" % (busy_op[0], max_wait_for_exclusive_lock),
                        "Attached is the traceback and the attempt to kill it.",
                        "Thread %s is the thread attempting to kill it, which will now take the Database Lock." % current_id
                        ])
                    Ratings.ratings.select(Notification.EmailAdmin).email_admin(email_msg, attach_contentlist=[(dump_file_contents, 'debug.htm', 'text/html')])
                    busy_op = None
                elif (time.time() - check_start_time > warning_timeout):
                    if not busy_op[3]:
                        # Warn of implending timeout
                        frame = ThreadDebug.find_thread_frame(busy_op[0])
                        last_trace_back = ThreadDebug.format_traceback(frame)
                        logging.warning("Thread %s still waiting for database lock after %ds - this may timeout", current_id, warning_timeout)
                        logging.info("\n".join(last_trace_back))
                        busy_op[3] = True
                    check_start_time = time.time()
            else:
                busy_op = now_busy_op
                check_start_time = time.time()

        # Element 4 here is whether this op has been warned for a potential timeout
        thread_busy[None] = [current_id, time.time(), 1, False]

def release_db_lock():
    with (database_write_lock):
        current_id = ThreadRaise.get_thread_id(threading.currentThread())
        busy_op = thread_busy.get(None, None)
        if busy_op and busy_op[0] == current_id:
            busy_op[2] -= 1
            if busy_op[2] <= 0:
                thread_busy.pop(None, None)
                database_write_lock.notify()

