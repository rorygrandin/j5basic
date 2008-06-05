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

def timedelta_to_tuple(timedelta):
    """Expresses a timedelta object as a tuple containing days, hours, minutes and seconds (rounded)"""
    d = timedelta.days
    s_total = timedelta.seconds
    h = s_total / 3600
    m = (s_total / 60) % 60
    s = s_total % 60
    return (d, h, m, s)

def tuple_to_timedelta(td_tuple):
    """Converts a days, hours, minutes and seconds tuple to a timedelta object"""
    d, h, m, s = td_tuple
    return datetime.timedelta(days=d, hours=h, minutes=m, seconds=s)

def timedelta_to_str(timedelta):
    """Expresses a timedelta as a human-readable string"""
    d, h, m, s = timedelta_to_tuple(timedelta)
    if d:
        return "%dd %02d:%02d:%02d" % (d, h, m, s)
    else:
        return "%02d:%02d:%02d" % (h, m, s)

def str_to_timedelta(td_str):
    """Parses a human-readable time delta string to a timedelta"""
    if "d" in td_str:
        day_str, time_str = td_str.split("d", 1)
        d = int(day_str.strip())
    else:
        time_str = td_str
        d = 0
    time_str = time_str.strip()
    if not time_str:
        return datetime.timedelta(days=d)
    colon_count = time_str.count(":")
    if (not colon_count) or colon_count > 2:
        raise ValueError("Time format [dd d] hh:mm[:ss] or dd d")
    elif colon_count == 1:
        h_str, m_str = time_str.split(":", 1)
        h, m, s = int(h_str.strip()), int(m_str.strip()), 0
    elif colon_count == 2:
        h_str, m_str, s_str = time_str.split(":", 2)
        h, m, s = int(h_str.strip()), int(m_str.strip()), int(s_str.strip())
    return tuple_to_timedelta((d, h, m, s))

def timetuple_to_datetime(t):
    """Convert a timetuple to a datetime object.
       """
    return datetime.datetime(*(t[:6]))

# deprecated alias
timetuple2datetime = timetuple_to_datetime

