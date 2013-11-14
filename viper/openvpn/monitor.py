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
"""
Service to manage and monitor OpenVPN on windows, this service uses RPCService
for interprocess communication.
"""
import rpyc
import subprocess
import os, sys, logging
from datetime import datetime
import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os, sys, string, time
import socket
import threading, time
from pprint import pprint
import psutil

from viper import routing
from viper.windows import service, firewall
from viper.tools import *
from viper.openvpn import management, launcher

import traceback


# global that keeps track of the current status
OVPN_STATUS = None
isstarting = False


class RPCService(rpyc.Service):
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.proc = None
        #self.monitor = None
        self.connected = False
        self.launcher = launcher.OpenVPNLauncher()

        logging.info("Connection from client opened...")
        # configure the Windows Firewall to block all IPv6 traffic
        firewall.block_ipv6()

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        logging.info("Connection from client closed")
        # allow IPv6 traffic again
        firewall.unblock_ipv6()

    def exposed_ovpn_start(self, cfgfile, logdir):
        """ Use launcher to start the OpenVPN instance 
        @param cfgfile location of OpenVPN configuration file in the file system
        @param logdir directory for log output
        """
        if not is_openvpn_running():
            logging.debug("OpenVPN isn't running, trying to start process")
            self.launcher.launch(cfgfile, logdir)
        else:
            logging.debug("Another instance of OpenVPN was found, sending SIGHUP to force restart")
            handle = management.OVPNInterface()
            handle.hangup()
            del handle
            # if it's already running try to reaload it by sending hangup signal

    def exposed_ovpn_stop(self):
        """ Use launcher to stop the OpenVPN process """
        self.launcher.terminate()

