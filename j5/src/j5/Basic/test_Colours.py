# -*- encoding: utf-8 -*-

from j5.Basic import Colours

def test_generate_colours():
    colours = Colours.get_colours(10)
    assert len(colours) == 10
    colours = Colours.get_colours(2)
    assert len(colours) == 2

