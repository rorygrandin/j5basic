#!/usr/bin/env python

from j5.Basic import Uid
import re

class TestUid(object):
    def test_uid_digit_str(self):
        ids = {}
        for i in range(10000):
            ids[Uid.uid_digit_str()] = None
        print len(ids)
        assert len(ids) == 10000 # no duplicates

        # check format
        uid_re = re.compile("[0-9]{17,22}")
        for uid in ids:
            if not uid_re.match(uid):
                print uid
                assert uid_re.match(uid)

    def test_uid_id_str(self):
        ids = {}
        for i in range(10000):
            ids[Uid.uid_id_str()] = None

        print len(ids)
        assert len(ids) == 10000 # no duplicates

        # check format
        uid_re = re.compile("ID[0-9]{17,22}")
        for uid in ids:
            if not uid_re.match(uid):
                print uid
                assert uid_re.match(uid)
