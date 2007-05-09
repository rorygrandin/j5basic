#!/usr/bin/env python

import datetime
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
        if isinstance(resolution, datetime.timedelta):
            self.resolution = resolution
        else:
            self.resolution = datetime.timedelta(seconds=resolution)

    def start(self):
        nexttime = datetime.datetime.now()
        self.stop = False
        while not self.stop:
            nexttime = nexttime + self.resolution
            currenttime = datetime.datetime.now()
            if nexttime < currenttime:
                logging.info("Timer function missed %s (at %s) - running behind schedule" % (nexttime, currenttime))
            else:
                waittime = nexttime - currenttime
                waitseconds = waittime.days * (24*60*60) + waittime.seconds + waittime.microseconds * 0.000001
                time.sleep(waitseconds)
            apply(self.target, self.args, self.kwargs)


if __name__ == "__main__":
    def print_time():
        print time.time()

    timer = Timer(print_time)
    timer.start()
