# -*- coding: utf-8 -*-

from __future__ import division
from j5.Basic import Units
import operator

def test_unit_class_creation():
    """Creation of Unit classes should successfully produce types"""
    m = Units.BaseUnit("m")
    assert isinstance(m, Units.Unit)
    # assert isinstance(m, type)

def test_unit_class_calculation():
    """Calculations on Units should result in derived Units"""
    m = Units.BaseUnit("m")
    mm = m / 1000
    assert isinstance(mm, Units.Unit)
    # assert isinstance(mm, type)
    # assert issubclass(mm, m)

    assert m / mm == Units.Unit("", {}, Units.Conversion(operator.mul, 1000))
    r = mm * 1000
    assert r.base_units == m.base_units
    assert r.op == m.op
    assert r == m
    assert mm * 1000 == m
    m_sq = m * m
    assert m_sq == m * m
    assert isinstance(m_sq, Units.Unit)
    # assert not issubclass(m_sq, m)

def test_unit_calculation():
    """tests that units created can be used in calculations"""
    m = Units.BaseUnit("m")
    mm = m / 1000
    x = m(35)
    assert x == mm(35000)

def test_unit_class_combination():
    """Calculations involving multiple Units should be consistent"""
    m = Units.BaseUnit("m")
    km = 1000 * m
    s = Units.BaseUnit("s")
    min = s * 60
    hour = min * 60
    m_per_s = m / s
    assert isinstance(m_per_s, Units.Unit)
    km_per_hour = km / hour
    # assert issubclass(km_per_hour, m_per_s)
    assert m_per_s(10) == km_per_hour(36)
    assert m_per_s(9) < km_per_hour(36)
    assert m_per_s(20) > km_per_hour(70)

