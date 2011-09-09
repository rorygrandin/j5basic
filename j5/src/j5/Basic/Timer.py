#!/usr/bin/env python

import datetime
import logging
import time
import threading

def to_seconds(timedelta):
    """Converts timedelta to a float number of seconds"""
    return timedelta.days * (24*60*60) + timedelta.seconds + timedelta.microseconds * 0.000001

class Timer(object):
    """Accurate timer of resolution minimum 1 second - the idea is to guarantee accuracy"""
    def __init__(self, target, args=None, kwargs=None, resolution=1):
        self.stop_event = threading.Event()
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

    def get_stop(self):
        return self.stop_event.isSet()

    def set_stop(self, new_stop):
        if new_stop:
            self.stop_event.set()
        else:
            self.stop_event.clear()

    stop = property(get_stop, set_stop)

    def start(self):
        nexttime = datetime.datetime.now()
        while not self.stop_event.isSet():
            nexttime = nexttime + self.resolution
            currenttime = datetime.datetime.now()
            if nexttime < currenttime:
                first_missed_time = nexttime
                missed_time_delta = currenttime - first_missed_time
                missed_count = int(to_seconds(missed_time_delta)/to_seconds(self.resolution))
                if missed_count > 0:
                    nexttime += missed_count * self.resolution
                logging.info("Timer function missed %04d ticks between %s and %s (at %s) - running behind schedule" % (missed_count+1, first_missed_time, nexttime, currenttime))
                nexttime += self.resolution
            else:
                while nexttime > currenttime and not self.stop_event.isSet():
                    waittime = nexttime - currenttime
                    waitseconds = to_seconds(waittime)
                    self.stop_event.wait(waitseconds)
                    currenttime = datetime.datetime.now()
            if not self.stop_event.isSet():
                apply(self.target, self.args, self.kwargs)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    def print_time():
        print time.time()

    timer = Timer(print_time)
    timer.start()
