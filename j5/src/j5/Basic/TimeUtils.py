from j5.Basic import TzInfo
import datetime

"""Utilities for dealing with time."""

def utcnow():
    """Return now in UTC with the tzinfo properly set."""
    dt = datetime.datetime.utcnow()
    dt = dt.replace(tzinfo=TzInfo.utc)
    return dt

def localsecondnow():
    """Provides the current local time with microseconds set to 0."""
    return datetime.datetime.now().replace(microsecond=0)

def localminutenow():
    """Provides the current local time with seconds and microseconds set to 0."""
    return datetime.datetime.now().replace(second=0,microsecond=0)

def totalseconds(timedelta):
    """Return the total number of seconds represented by a datetime.timedelta object."""
    return timedelta.seconds + (timedelta.days * 24 * 60 * 60)

def totalhours(timedelta):
    """Return the total number of hours represented by a datetime.timedelta object."""
    return float(totalseconds(timedelta)) / 3600

def hoursandminutes(timedelta):
    """Expresses a timedelta object as a tuple containing hours and minutes.  Seconds are rounded."""
    th = totalhours(timedelta)
    wh = int(th)
    tm = (th - wh) * 60
    wm = int(tm)

    return (wh,wm)

def timetuple2datetime(t):
    """Convert a timetuple to a datetime object.
       """
    return datetime.datetime(*(t[:6]))
