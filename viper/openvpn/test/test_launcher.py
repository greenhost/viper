#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

    def tearDown(self):
    	pass

    def test_launch(self):
    	launcher = OpenVpnLauncher()
        launcher.launch(self.cfgfile)

    def test_terminate(self):
        launcher = OpenVpnLauncher()
        launcher.terminate()

if __name__ == "__main__":
    unittest.main()
