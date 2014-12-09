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
Service to manage and monitor OpenVPN on windows
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
from viper.windows import service
from viper.openvpn import monitor
from viper.tools import *
import traceback


# see this http://tebl.homelinux.com/view_document.php?view=6
# for the only successful howto I could find
class OVPNService(win32serviceutil.ServiceFramework):
    """Windows Service implementation. Starts a RPyC server listening to
    connections on port 18861 from localhost only.

    """
    _svc_name_ = 'ovpnmon'
    _svc_display_name_ = 'OVPN monitor'
    _svc_description_ = 'Monitor the OpenVPN client on this machine'

    def __init__(self, *args):
        logging.getLogger('').handlers = []   # clear any existing log handers
        log_init_service()
        win32serviceutil.ServiceFramework.__init__(self, *args)
        logging.info('init')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.runflag = False

        try:
            from viper.backend import http
        except Exception, e:
            logging.critical("Couldn't import runtime entry point")
        # start serving HTTP
        self.svc = http.init(debug=False)
        logging.info("Viper service is running")


    def sleep(self, sec):
        win32api.Sleep(sec*1000, True)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            logging.info('start')
            self.start()
            logging.info('wait')
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            logging.info('done')
        except Exception, x:
            logging.warning('Exception : %s' % x)
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        logging.info('stopping')
        self.stop()
        logging.info('stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    # to be overridden
    def start(self):        
        logging.info("OVPN monitoring service starting...")
        self.svc.serve(host='127.0.0.1', port=8088)
        self.runflag = True

        # while self.runflag:
        #     self.sleep(10)
        #     logging.debug("Service is alive ...")

    # to be overridden
    def stop(self):
        logging.info("OVPN monitoring service shutting down...")
        # TODO no way to stop http server yet
        #self.svc.close()
        self.runflag = False
