#!/usr/bin/env python

import os
from j5basic import Module
from j5test import Utils

class TestModule:
    def test_find_module(self):
        target_file = Module.__file__
        if target_file.endswith(".pyc") or target_file.endswith(".pyo"):
            source_file = target_file[:target_file.rfind(".")] + ".py"
            if os.path.exists(source_file):
                target_file = source_file
        assert Module.find_module("j5basic") == os.path.dirname(target_file)
        assert Module.find_module("j5basic.Module") == target_file
        assert Utils.raises(ValueError, Module.find_module, "j5basic.NonExistent")

    def test_resolve(self):
        assert Module.resolvemodule("j5basic.Module") == Module
        from j5.Config import ConfigTree
        assert Module.resolvemodule("j5.Config.ConfigTree.Node") == ConfigTree.Node

