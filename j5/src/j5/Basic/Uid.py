#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions for generating unique ids.
   
   Although this doesn't implement it, it's worthwhile reading RFC 4122 [1],
   "A Universally Unique IDentifier (UUID) URN Namespace" for some thoughts
   on the subject. At some point we could look at implementing RFC 4122 here,
   or replacing these functions with calls to an external RFC 4122 implementation.
   
   [1] http://www.rfc-archive.org/getrfc.php?rfc=4122
   """

# Copyright 2006 St James Software

__all__ = ["str_uid"]

import time
import random

def uid_digit_str():
    """Returns a unique string consisting only of digits.
       Generated using the current time and a random integer
       between 1 and 10**6."""
    return str(int(time.time()*10**6)) + str(random.randint(1,10**6))
