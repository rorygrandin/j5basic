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

def totalseconds(timedelta):
    """Return the total number of seconds represented by a datetime.timedelta object."""
    return timedelta.seconds + (timedelta.days * 24 * 60 * 60)
