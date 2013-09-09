#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Greenhost vof
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

    def exposed_heartbeat(self):
        return str(datetime.now())

    def exposed_is_connected(self):
        global OVPN_STATUS
        OVPN_STATUS = management.poll_status()
        return (OVPN_STATUS['status'] == "CONNECTED")

    def exposed_get_vpn_status(self):
        global OVPN_STATUS
        OVPN_STATUS = management.poll_status()
        return OVPN_STATUS['status']

    def exposed_get_connection_settings(self):
        global OVPN_STATUS
        OVPN_STATUS = management.poll_status()
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS
        else:
            return None

    def exposed_get_gateway_ip(self):
        pass

    def exposed_get_interface_ip(self):
        pass

    def exposed_ovpn_start(self, cfgfile):
        """Use launcher to start the OpenVPN instance
        an exception of type VPNLauncherException may be raised
        it's best not to handle it here but in the client so that
        we can notify the user.
        """
        self.launcher.launch(cfgfile)



    def exposed_ovpn_stop(self):
        """Use launcher to stop the OpenVPN process"""
        self.launcher.terminate()

