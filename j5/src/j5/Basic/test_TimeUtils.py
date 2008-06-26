from j5.Basic import TimeUtils
from j5.Test import Utils
import datetime

def test_timedelta_roundtrip():
    timedelta = datetime.timedelta(days=5,hours=23,minutes=12,seconds=59)
    timetuple = TimeUtils.timedelta_to_tuple(timedelta)
    assert timetuple == (5,23,12,59)
    assert TimeUtils.tuple_to_timedelta(timetuple) == timedelta

def test_strftime():
    """Tests the adjusted strftime works with dates before 1900"""
    assert TimeUtils.strftime(datetime.datetime(1996,9,3,12,51,50), "%Y:%m:%d %H:%M:%S") == "1996:09:03 12:51:50"
    assert TimeUtils.strftime(datetime.datetime(1896,9,3,12,51,50), "%Y:%m:%d %H:%M:%S") == "1896:09:03 12:51:50"
    assert TimeUtils.strftime(datetime.datetime(1818,9,18,18,18,18), "%Y%m%d%H%M%S") == "18180918181818"
    assert TimeUtils.strftime(datetime.datetime(1822,9,22,22,22,22), "%Y%m%d%H%M%S") == "18220922222222"
    assert TimeUtils.strftime(datetime.datetime(1822,9,22,22,22,22), "%%Y%m%d%H%M%S") == "%Y0922222222"

def always_skip(*args, **kwargs):
    return True

@Utils.skip_test_for("This test is too slow to run by default", always_skip)
def test_sequence():
    """Checks that the day names are in order from 1/1/1 until August 2000"""
    # from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/306860
    s = TimeUtils.strftime(datetime.date(1800, 9, 23),
                 "%Y has the same days as 1980 and 2008")
    if s != "1800 has the same days as 1980 and 2008":
        raise AssertionError(s)

    print "Testing all day names from 0001/01/01 until 2000/08/01"
    # Get the weekdays.  Can't hard code them; they could be
    # localized.
    days = []
    for i in range(1, 10):
        days.append(datetime.date(2000, 1, i).strftime("%A"))
    nextday = {}
    for i in range(8):
        nextday[days[i]] = days[i+1]

    startdate = datetime.date(1, 1, 1)
    enddate = datetime.date(2000, 8, 1)
    prevday = TimeUtils.strftime(startdate, "%A")
    one_day = datetime.timedelta(1)

    testdate = startdate + one_day
    while testdate < enddate:
        if (testdate.day == 1 and testdate.month == 1 and
            (testdate.year % 100 == 0)):
            print "Testing century", testdate.year
        day = TimeUtils.strftime(testdate, "%A")
        if nextday[prevday] != day:
            raise AssertionError(str(testdate))
        prevday = day
        testdate = testdate + one_day

