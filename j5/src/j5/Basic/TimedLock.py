#!/usr/bin/env python

import threading
import time

class TimedLock(threading._RLock):
    """A lock that allows waiting"""
    def __init__(self):
        self._wait_event = threading.Event()
        self._wait_event.set()
        super(TimedLock, self).__init__()

    def acquire(self, wait=True):
        """Tries to acquire the lock
        If wait is True (default), block until the lock is available
        If wait is a number, wait the given number of seconds before giving up
        If wait is non-True (None, False, or zero), acquire non-blocking"""
        name = threading.current_thread().name
        if wait is True:
            super(TimedLock, self).acquire(True)
            self._wait_event.clear()
            return True
        elif not wait:
            if super(TimedLock, self).acquire(False):
                self._wait_event.clear()
                return True
            return False
        else:
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time < wait:
                self._wait_event.wait(wait - elapsed_time)
                if super(TimedLock, self).acquire(False):
                    self._wait_event.clear()
                    return True
                elapsed_time = time.time() - start_time
            return False

    def release(self):
        """Releases the lock and notifies any waiting threads"""
        super(TimedLock, self).release()
        self._wait_event.set()

