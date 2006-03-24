#!/usr/bin/env python

from Basic import Timer
import threading
import time

class TimerDriver:
    def __init__(self, expecteddiff=1, expectarg=False):
        self.lasttime = None
        self.expecteddiff = expecteddiff
        self.expectarg = expectarg

    def timefunc(self, testarg=None):
        tm = time.time()
        assert not self.expectarg or testarg is not None
        if self.lasttime != None:
            assert tm - self.lasttime == self.expecteddiff
        self.lasttime = tm

class TestTimer:
    def test_onesec(self):
        """Test the one second resolution"""
        tm = TimerDriver()
        timer = Timer.Timer(tm.timefunc)
        thread = threading.Thread(target=timer.start)
        thread.start()
        time.sleep(3)
        timer.stop = True
        assert tm.lasttime is not None

    def test_twosec(self):
        """Test a non one second resolution"""
        tm = TimerDriver(2)
        timer = Timer.Timer(tm.timefunc, resolution=2)
        thread = threading.Thread(target=timer.start)
        thread.start()
        time.sleep(5)
        timer.stop = True
        assert tm.lasttime is not None

    def test_args(self):
        """Test passing args"""
        tm = TimerDriver(expectarg=True)
        timer = Timer.Timer(tm.timefunc, args=(True,))
        thread = threading.Thread(target=timer.start)
        thread.start()
        time.sleep(3)
        timer.stop = True
        assert tm.lasttime is not None

    def test_kwargs(self):
        """Test passing kwargs"""
        tm = TimerDriver(expectarg=True)
        timer = Timer.Timer(tm.timefunc, kwargs={"testarg":True})
        thread = threading.Thread(target=timer.start)
        thread.start()
        time.sleep(3)
        timer.stop = True
        assert tm.lasttime is not None

