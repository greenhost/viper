#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Greenhost VOF and contributors
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.
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
