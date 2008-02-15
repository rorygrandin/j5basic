#!/usr/bin/env python

import datetime
import time
import logging

def to_seconds(timedelta):
    """Converts timedelta to a float number of seconds"""
    return timedelta.days * (24*60*60) + timedelta.seconds + timedelta.microseconds * 0.000001

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
                first_missed_time = nexttime
                missed_time_delta = currenttime - first_missed_time
                missed_count = int(to_seconds(missed_time_delta)/to_seconds(self.resolution))
                nexttime += (missed_count - 1) * self.resolution
                logging.info("Timer function missed %d ticks between %s and %s (at %s) - running behind schedule" % (missed_count, first_missed_time, nexttime, currenttime))
                nexttime += self.resolution
            else:
                waittime = nexttime - currenttime
                waitseconds = to_seconds(waittime)
                time.sleep(waitseconds)
            apply(self.target, self.args, self.kwargs)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    def print_time():
        print time.time()

    timer = Timer(print_time)
    timer.start()

