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
    """ This service performs all the operations that have to run with elevated privileges, such as
    starting and stopping OpenVPN and interacting with firewall rules.
    """
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.proc = None
        #self.monitor = None
        self.connected = False
        self.launcher = launcher.OpenVPNLauncher()

        logging.info("Connection from client opened...")

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        logging.info("Connection from client closed")

    def exposed_ovpn_start(self, cfgfile, logdir):
        """ Use launcher to start the OpenVPN instance 
        @param cfgfile location of OpenVPN configuration file in the file system
        @param logdir directory for log output
        """
        if not is_openvpn_running():
            logging.debug("OpenVPN isn't running, trying to start process")

            # configure the Windows Firewall to block all IPv6 traffic
            #firewall.block_ipv6()
            self.launcher.launch(cfgfile, logdir)
            # @TODOlaunch is async, perhaps this should be a callback
            #firewall.block_default_gateway()
        else:
            logging.debug("Another instance of OpenVPN was found, sending SIGHUP to force restart")
            handle = management.OVPNInterface()
            handle.hangup()
            del handle
            # if it's already running try to reaload it by sending hangup signal

    def exposed_firewall_up(self):
        """ Activate the firewall rules that will enhance the user's protection through the duration of the VPN run """
        logging.debug("Putting up firewall")
        # configure the Windows Firewall to block all IPv6 traffic
        firewall.block_ipv6()
        # @TODO launch is async, perhaps this should be a callback
        firewall.block_default_gateway("none-specified")

    def exposed_firewall_down(self):
        """ Deactivate the firewall rules """
        logging.debug("Taking down firewall")
        # allow IPv6 traffic again
        firewall.unblock_ipv6()
        firewall.unblock_default_gateway("none-specified")

    def exposed_set_default_gateway(self, gwip):
        logging.debug("Setting default gateway to '{0}'".format(gwip))
        routing.route_add("0.0.0.0", "0.0.0.0", gwip)

    def exposed_ovpn_stop(self):
        """ Use launcher to stop the OpenVPN process """
        self.launcher.terminate()

