#!/usr/bin/env python

"""Tests WithContextSkip"""

from . import WithContextSkip

SkipDetector = WithContextSkip.StatementSkippedDetector

@WithContextSkip.conditionalcontextmanager
def wanneer(condition):
    if condition:
        yield

@WithContextSkip.conditionalcontextmanager
def if_positive(value):
    if value > 0:
        yield value

def test_no_value_condition_avoided():
    """Tests that the generator not yielding means the code block governed by with is not run, with no value being assigned by the with statement"""
    code_run = False
    with wanneer(False) as SkipDetector.detect:
        code_run = True
    assert not code_run

def test_no_value_condition_passed():
    """Tests that the generator yielding means the code block governed by with is run, with no value being assigned by the with statement"""
    code_run = False
    with wanneer(True) as SkipDetector.detect:
        code_run = True
    assert code_run

def test_ignored_value_condition_passed():
    """Tests that the generator yielding means the code block governed by with is run, with a value being yielded by the generator but ignored"""
    code_run = False
    with if_positive(37) as SkipDetector.detect:
        code_run = True
    assert code_run

def test_ignored_value_condition_avoided():
    """Tests that the generator not yielding means the code block governed by with is not run, with a value being yielded by the generator but ignored"""
    code_run = False
    with if_positive(-37) as SkipDetector.detect:
        code_run = True
    assert not code_run

def test_received_value_condition_passed():
    """Tests that the generator yielding means the code block governed by with is run, with a value being yielded by the generator and received"""
    code_run = False
    with if_positive(37) as (value, SkipDetector.detect):
        code_run = True
        assert value == 37
    assert value == 37
    assert code_run

def test_received_value_condition_avoided():
    """Tests that the generator not yielding means the code block governed by with is not run, with StatementSkipped being received by the target value variable"""
    code_run = False
    with if_positive(-37) as (value, SkipDetector.detect):
        code_run = True
    assert not code_run
    assert value is WithContextSkip.StatementSkipped


