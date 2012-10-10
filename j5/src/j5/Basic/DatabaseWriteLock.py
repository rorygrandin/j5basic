# -*- coding: utf-8 -*-

"""Module for write locks to do with databases.  When this is no longer used, we're ready for multiprocess database writes"""

import threading
import logging
from collections import deque, namedtuple
from j5.OS import ThreadRaise
from j5.OS import ThreadDebug
from j5.Logging import Errors
from j5.Control.Interface import Notification, Server, Admin
from j5.Control import Ratings, InterfaceRegistry
from j5.Text.Conversion import wiki2html
# instead of using time.time, use the always-unpatched version (so that VirtualTime will not affect this module)
from j5.Test import VirtualTime
nonvirtual_time = VirtualTime._original_time # time.time, without virtual time patching

database_write_lock = threading.Condition()
database_lock_queue = deque()
MAX_LOCK_WAIT_TIMEOUT = 120
LOCK_WARNING_TIMEOUT = 30

class ServerMode(InterfaceRegistry.Component):
    """Component that allows following what mode the server is in"""
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
    """Decorator that annotates a function to indicate it doesn't perform any database write operations and doesn't require the database write lock"""
    f.requires_database_lock = False
    return f

def requires_database_lock(f):
    """Decorator that annotates a function to indicate it performs database write operations and requires the database write lock"""
    f.requires_database_lock = True
    return f

class LockRequest(object):
    def __init__(self, thread, request_time):
        self.thread = thread
        self.request_time = request_time
        self.count = 1
        self.warning_issued = False
        self.start_time = None

def get_db_lock(max_wait_for_exclusive_lock=MAX_LOCK_WAIT_TIMEOUT, warning_timeout=LOCK_WARNING_TIMEOUT):
    """Acquire the database for use in operations that may result in writing and require exclusive access under our current conservative model"""
    current_thread = threading.currentThread()
    if ServerMode().mode == Admin.ServerModeEnum.SLAVE:
        logging.error("Requesting DatabaseWriteLock on SLAVE process.  Traceback in info logs")
        try:
            frame = ThreadDebug.find_thread_frame(ThreadRaise.get_thread_id(current_thread))
            last_trace_back = ThreadDebug.format_traceback(frame)
            logging.info("\n".join(last_trace_back))
        except Exception, e:
            logging.warning("Error logging traceback for DatabaseWriteLock SLAVE operation: %r", e)
    left_for_dead_thread = None

    with (database_write_lock):
        if database_lock_queue:
            busy_op = database_lock_queue[0]
            if busy_op.thread is current_thread:
                # Multi-entrant
                busy_op.count += 1
                return

        # This is used to measure the max time for timeout purposes
        start_time = nonvirtual_time()
        # This is used to make sure we don't wait too long on the notify
        check_start_time = start_time

        database_lock_queue.append(LockRequest(current_thread, start_time))

        while database_lock_queue[0].thread is not current_thread:
            logging.info('Thread %s waiting for Thread %s to release database lock (maximum wait %ds)',
                current_thread, database_lock_queue[0].thread, max_wait_for_exclusive_lock)

            database_write_lock.wait(warning_timeout)

            # Check if I'm still blocked:
            if database_lock_queue[0].thread is not current_thread:

                # Check if I'm next in the queue;
                if database_lock_queue[1].thread is current_thread:
                    # It's the responsibility of the next-in-line thread to monitor for excess lock times; we assume that this thread will keep on waiting and performing this function until it acquires the lock
                    busy_op = database_lock_queue[0]
                    if busy_op.start_time:
                        busy_op_time = nonvirtual_time() - busy_op.start_time
                        if busy_op_time > max_wait_for_exclusive_lock:
                            # Forcibly release the lock:
                            # On the next round in to the loop, we'll exit and continue
                            logging.critical("Thread %s has had the database write lock for %ds - forcing it to drop it (%s)", busy_op.thread, busy_op_time, current_thread)
                            database_lock_queue.popleft()
                            # We're going to ignore this thread and take the lock anyway
                            left_for_dead_thread = busy_op.thread
                        if busy_op_time > warning_timeout:
                            if not busy_op.warning_issued:
                                try:
                                    # Warn of impending timeout
                                    frame = ThreadDebug.find_thread_frame(ThreadRaise.get_thread_id(busy_op.thread))
                                    last_trace_back = ThreadDebug.format_traceback(frame)
                                    logging.warning("Thread %s still waiting for database lock after %ds - this may timeout", current_thread, warning_timeout)
                                    logging.info("\n".join(last_trace_back))
                                    busy_op.warning_issued = True
                                except Exception as e:
                                    logging.error("Exception occurred while trying to warn Database Lock timeout on thread %s - %s",current_thread, e)

        # record the time we got the lock
        database_lock_queue[0].start_time = nonvirtual_time()

    # Outside the database_write_lock, as this can take a while
    if left_for_dead_thread:
        try:
            # Time to steal the lock from this
            traceback_lines = ["=== Tracebacks from blocking thread that lock was taken from==="]
            logging.error('Thread %s timed out waiting for Thread %s to release database lock ... Stealing lock ...',
                current_thread, left_for_dead_thread)
            frame = ThreadDebug.find_thread_frame(ThreadRaise.get_thread_id(left_for_dead_thread))
            last_trace_back = ThreadDebug.format_traceback(frame)
            logging.info("Traceback of stuck thread:\n%s","\n".join(last_trace_back))
            traceback_lines.append("== Traceback of stuck thread %s ==" % left_for_dead_thread)
            traceback_lines.append("{{{")
            traceback_lines.extend(last_trace_back)
            traceback_lines.append("}}}")
            dump_file_contents = wiki2html.creole2xhtml("\n".join(traceback_lines))
            email_msg = "\n".join([
                "== Blocking Thread in Database Lock ==",
                "The thread %s has blocked the Database Lock for over %ds" % (left_for_dead_thread, max_wait_for_exclusive_lock),
                "Attached is the traceback - the database lock has been stolen as we assume this thread is dead",
                "Thread %s is the thread which will now take the Database Lock." % current_thread
            ])
            email_admin = Ratings.ratings.select(Notification.EmailAdmin)
            if email_admin:
                email_admin.email_admin(email_msg, attach_contentlist=[(dump_file_contents, 'debug.htm', 'text/html')])
            else:
                logging.error("No admin emailer while trying to send details of stuck thread")
        except Exception as e:
            logging.error("Error creating / sending error email for thread %s we're trying to steal the database lock from - %s",left_for_dead_thread, e)

def release_db_lock():
    current_thread = threading.currentThread()
    with (database_write_lock):
        if database_lock_queue:
            busy_op = database_lock_queue[0]
            if busy_op.thread is current_thread:
                busy_op.count -= 1
                if busy_op.count <= 0:
                    database_lock_queue.popleft()
                    database_write_lock.notifyAll()
                    return
    logging.error("Thread %s came out of the database write lock but wasn't the busy operation any more - it either had the lock stolen due to being stuck or the lock is being released twice by coding error", current_thread)


