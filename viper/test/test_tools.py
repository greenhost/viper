#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Greenhost VOF
# https://greenhost.nl -\- https://greenhost.io
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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
