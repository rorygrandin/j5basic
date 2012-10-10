# -*- coding: utf-8 -*-

"""Module for write locks to do with databases.  When this is no longer used, we're ready for multiprocess database writes"""

import threading
import logging
import time
from collections import deque
from j5.OS import ThreadRaise
from j5.OS import ThreadDebug
from j5.Logging import Errors
from j5.Control.Interface import Notification, Server, Admin
from j5.Control import Ratings, InterfaceRegistry
from j5.Text.Conversion import wiki2html

database_write_lock = threading.Condition()
database_lock_queue = deque()
MAX_LOCK_WAIT_TIMEOUT = 120
LOCK_WARNING_TIMEOUT = 30

class ServerMode(InterfaceRegistry.Component):
    InterfaceRegistry.implements(Server.ResourceInterface)
    def startup(self, get_resource):
        """Called at server startup"""
        self.server = get_resource("DatabaseLock", "server")

    def cleanup(self, cleanup_resource):
        """Called at server shutdown"""
        pass

    def get_mode(self):
        return self.server.mode
    mode = property(get_mode)

class DatabaseLockTooLong(RuntimeError):
    pass

def no_database_writes(f):
    f.requires_database_lock = False
    return f

def requires_database_lock(f):
    f.requires_database_lock = True
    return f

#Busy Op Indexes
_THREAD_ID = 0
_LOCK_ACQUIRED_TIME = 1
_LOCK_COUNT = 2
_WARNING_DONE = 3

def get_db_lock(max_wait_for_exclusive_lock=MAX_LOCK_WAIT_TIMEOUT, warning_timeout=LOCK_WARNING_TIMEOUT):
    current_id = ThreadRaise.get_thread_id(threading.currentThread())
    if ServerMode().mode == Admin.ServerModeEnum.SLAVE:
        logging.error("Requesting DatabaseWriteLock on SLAVE process.  Traceback in info logs")
        frame = ThreadDebug.find_thread_frame(current_id)
        last_trace_back = ThreadDebug.format_traceback(frame)
        logging.info("\n".join(last_trace_back))
    kill_thread_id = None
    email_msg = None
    dump_file_contents = None

    with (database_write_lock):
        if database_lock_queue:
            busy_op = database_lock_queue[0]
            if busy_op[_THREAD_ID] == current_id:
                # Multi-entrant
                busy_op[_LOCK_COUNT] += 1
                return

        # This is used to measure the max time for timeout purposes
        start_time = time.time() #TODO: We should probably be using virtual time's underlying time for this (see davidf's recent commits for deadlock detection)
        # This is used to make sure we don't wait too long on the notify
        check_start_time = start_time

        database_lock_queue.append([current_id, start_time, 1, False])

        while database_lock_queue[0][_THREAD_ID] != current_id:
            busy_op = database_lock_queue[0]
            logging.info('Thread %s waiting for Thread %s to release database lock (maximum wait %ds)',
                current_id, busy_op[_THREAD_ID], max_wait_for_exclusive_lock)

            database_write_lock.wait(warning_timeout)

            # Check if I'm still blocked:
            if database_lock_queue[0][_THREAD_ID] != current_id:

                # Check if I'm next in the queue;
                if database_lock_queue[1][_THREAD_ID] == current_id:
                    new_busy_op = database_lock_queue[0]
                    if new_busy_op is not busy_op:
                        busy_op = new_busy_op
                        check_start_time = time.time()
                    else:
                        # Make sure we've waited the timeout time, as the same thread can release and catch the lock multiple times
                        if (time.time() - start_time > max_wait_for_exclusive_lock):
                            #Release the lock:
                            #On the next round in to the loop, we'll exit and continue
                            database_lock_queue.popleft()

                            #We're going to kill this (once we've got the lock, and released the database_write_lock condition
                            kill_thread_id = busy_op[_THREAD_ID]
                        elif (time.time() - check_start_time > warning_timeout):
                            if not busy_op[_WARNING_DONE]:
                                try:
                                    # Warn of impending timeout
                                    frame = ThreadDebug.find_thread_frame(busy_op[_THREAD_ID])
                                    last_trace_back = ThreadDebug.format_traceback(frame)
                                    logging.warning("Thread %s still waiting for database lock after %ds - this may timeout", current_id, warning_timeout)
                                    logging.info("\n".join(last_trace_back))
                                    busy_op[_WARNING_DONE] = True
                                except Exception as e:
                                    logging.error("Exception occurred while trying to warn Database Lock timeout on thread %s - %s",current_id, e)

    # Outside the database_write_lock, as this can take a while
    if kill_thread_id:
        try:
            # Time to kill this
            traceback_lines = ["=== Tracebacks from attempt to kill blocking thread==="]
            frame = ThreadDebug.find_thread_frame(kill_thread_id)
            last_trace_back = ThreadDebug.format_traceback(frame)
            logging.error('Thread %s timed out waiting for Thread %s to release database lock ... Killing blocking thread ...',
                current_id, kill_thread_id)
            logging.info("Traceback of thread to be killed:\n%s","\n".join(last_trace_back))
            try:
                ThreadRaise.thread_async_raise(kill_thread_id, DatabaseLockTooLong)
                traceback_lines.append("== DatabaseLockTooLong exception raised in Thread %s ==" % kill_thread_id)
            except Exception as e:
                msg = "Could not raise exception in thread %s - %e" % (kill_thread_id, e)
                logging.error(msg)
                traceback_lines.append("== %s ==" % msg)
                tb = Errors.traceback_str()
                logging.info(tb)
                traceback_lines.append("{{{")
                traceback_lines.extend(tb.split("\n"))
                traceback_lines.append("}}}")
            traceback_lines.append("== Traceback of killed thread %s ==" % kill_thread_id)
            traceback_lines.append("{{{")
            traceback_lines.extend(last_trace_back)
            traceback_lines.append("}}}")
            dump_file_contents = wiki2html.creole2xhtml("\n".join(traceback_lines))
            email_msg = "\n".join([
                "== Blocking Thread in Database Lock ==",
                "The thread %s has blocked the Database Lock for over %ds" % (kill_thread_id, max_wait_for_exclusive_lock),
                "Attached is the traceback and the attempt to kill it.",
                "Thread %s is the thread attempting to kill it, which will now take the Database Lock." % current_id
            ])
            email_admin = Ratings.ratings.select(Notification.EmailAdmin)
            if email_admin:
                email_admin.email_admin(email_msg, attach_contentlist=[(dump_file_contents, 'debug.htm', 'text/html')])
            else:
                logging.error("No admin emailer while trying to send details of killed thread")
        except Exception as e:
            logging.error("Error creating / sending error email for thread %s we're trying to kill - %s",kill_thread_id,e)

def release_db_lock():
    current_id = ThreadRaise.get_thread_id(threading.currentThread())
    with (database_write_lock):
        if database_lock_queue:
            busy_op = database_lock_queue[0]
            if busy_op[_THREAD_ID] == current_id:
                busy_op[_LOCK_COUNT] -= 1
                if busy_op[_LOCK_COUNT] <= 0:
                    database_lock_queue.popleft()
                    database_write_lock.notifyAll()

