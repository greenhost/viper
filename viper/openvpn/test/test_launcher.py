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

from viper.openvpn import launcher

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class LauncherTest(unittest.TestCase):
    def setUp(self):
        self.cfgfile = os.path.join(os.path.split(__file__)[0], "badconfig.ovpn")
        print self.cfgfile

    def tearDown(self):
    	pass

    def test_bad_config(self):
    	ovpn = launcher.OpenVPNLauncher()
        try:
            ovpn.launch(self.cfgfile)
            self.fail("OpenVPN was launched with  a bad config file and no exception has been thrown")
        except launcher.VPNLauncherException, e:
            pass
        except e:
            self.fail('Unexpected exception thrown:', e)

    def test_missing_ovpn_executable(self):
        pass

    def test_terminate(self):
        ovpn = launcher.OpenVPNLauncher()
        ovpn.terminate()

if __name__ == "__main__":
    logging.basicConfig( stream=sys.stderr )
    #logging.getLogger( "SomeTest.testSomething" ).setLevel( logging.DEBUG )
    unittest.main()
