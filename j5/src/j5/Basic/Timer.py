#!/usr/bin/env python

import time
import logging

class Timer:
    """Accurate timer of resolution minimum 1 second - the idea is to guarantee accuracy"""
    def __init__(self, target, args=None, kwargs=None, resolution=1):
        self.target = target
        self.args = args
        if self.args is None:
            self.args = ()
        self.kwargs = kwargs
        if self.kwargs is None:
            self.kwargs = {}
        self.resolution = resolution

    def start(self):
        nexttime = time.time()
        self.stop = False
        while not self.stop:
            nexttime = nexttime + self.resolution
            if nexttime < time.time():
                logging.warning("Timer function too slow for resolution - attempting to catch up")
            else:
                time.sleep(nexttime - time.time())
            apply(self.target, self.args, self.kwargs)


if __name__ == "__main__":
    def print_time():
        print time.time()

    timer = Timer(print_time)
    timer.start()
