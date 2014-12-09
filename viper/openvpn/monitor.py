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
from viper.reactor import Reactor
import traceback


# global that keeps track of the current status
OVPN_STATUS = None
isstarting = False

class RPCService(rpyc.Service):
    """ Rpyc wrapper for Reactor """
    reactor = Reactor()
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        logging.info("Connection from client opened...")

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        logging.info("Connection from client closed")

    def exposed_ovpn_start(self, cfgfile, logdir):
        reactor.tunnel_open(cfgfile, logdir)

    def exposed_ovpn_stop(self):
        reactor.tunnel_close()

    def exposed_firewall_up(self):
        reactor.firewall_up()

    def exposed_firewall_down(self):
        reactor.firewall_down()

    def exposed_set_default_gateway(self, gwip):
        reactor.set_default_gateway()


