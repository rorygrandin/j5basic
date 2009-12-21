#!/usr/bin/env python

import threading
import time

class TimedLock(threading._RLock):
    """A lock that allows waiting"""
    def __init__(self):
        self._wait_event = threading.Event()
        self._wait_event.set()
        super(TimedLock, self).__init__()

    def acquire(self, wait=None):
        """Tries to acquire the lock. If a wait is specified, wait the given amount of time before giving up. Otherwise, is non-blocking"""
        name = threading.current_thread().name
        if wait is not None:
            start_time = time.time()
            elapsed_time = 0
            while elapsed_time < wait:
                self._wait_event.wait(wait - elapsed_time)
                if super(TimedLock, self).acquire(False):
                    self._wait_event.clear()
                    return True
                elapsed_time = time.time() - start_time
            return False
        else:
            if super(TimedLock, self).acquire(False):
                self._wait_event.clear()
                return True
            return False

    def release(self):
        """Releases the lock and notifies any waiting threads"""
        super(TimedLock, self).release()
        self._wait_event.set()

