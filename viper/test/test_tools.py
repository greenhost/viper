#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import psutil

from viper import tools

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class ToolsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
    	pass

    # def test_instance_check_running(self):
    #     res = tools.is_viper_running()
    #     self.assertTrue(res, "Another instance is running")

    def test_instance_check_stale(self):
        res = tools.is_viper_running()
        self.assertFalse(res, "The PID file is stale")

    # def test_instance_check_not_running(self):
    #     res = tools.is_viper_running()
    #     self.assertFalse(res, "No running instances")

if __name__ == "__main__":
    logging.basicConfig( stream=sys.stderr )
    unittest.main()
