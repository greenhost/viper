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
from viper.windows import service
from viper.tools import *
from viper.openvpn import management, launcher

import traceback


# global that keeps track of the current status
OVPN_STATUS = None


class RPCService(rpyc.Service):
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.proc = None
        #self.monitor = None
        self.connected = False
        logging.info("Connection from client opened...")

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        logging.info("Connection from client closed")

    def exposed_heartbeat(self):
        return str(datetime.now())

    def exposed_is_connected(self):
        global OVPN_STATUS
        OVPN_STATUS = ovpn.poll_status()
        return (OVPN_STATUS['status'] == "CONNECTED")

    def exposed_get_vpn_status(self):
        global OVPN_STATUS
        OVPN_STATUS = ovpn.poll_status()
        return OVPN_STATUS['status']

    def exposed_get_connection_settings(self):
        global OVPN_STATUS
        OVPN_STATUS = ovpn.poll_status()
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS
        else:
            return None

    def exposed_get_gateway_ip(self):
        pass

    def exposed_get_interface_ip(self):
        pass

    def exposed_ovpn_start(self, cfgfile):
        global OVPN_STATUS
        logging.debug("Start on manager thread called, ready to call OpenVPN")
        path = get_openvpn_home()
        path = os.path.join(path, "openvpn")

        cmd = "%s %s" % (path, cfgfile)
        logging.debug("Trying to execute OpenVPN client %s" % (cmd,))
        f = open(os.devnull, 'w')

        try:
            self.proc = subprocess.Popen([path, cfgfile], stdout=f, stderr=f)
            # check return code (e.g. OpenVPN fails to start is the config file is malformed, Viper doesn't report that condition in any way yet)
            if self.proc.returncode != 0:
                logging.error("Executing external OpenVPN process failed returning %s" % (self.proc.returncode,))
        except EnvironmentError, e:
            # @todo check if the exception above is actually raised by subprocess.Popen
            logging.critical("Couldn't execute subprocess '%s'" % (path,))


    def exposed_ovpn_stop(self):
        logging.debug("Terminating OpenVPN subprocess")
        # terminate openvpn processes
        try:
            procs = is_openvpn_running()
            if procs: # process found, terminate it
                for p in procs:
                    p.terminate()  # NoSuchProcess: process no longer exists (pid=2476)
        except (psutil.NoSuchProcess, psutil.AccessDenied), err:
            logging.error("exception while trying to shut down OpenVPN process for pid:%s, reason:%s" % (err.pid, err.msg))


