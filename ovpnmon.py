#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Greenhost vof
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

from win import routing
from win import service
from win.tools import *
import ovpn
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

        self.proc = subprocess.Popen([path, cfgfile], stdout=f, stderr=f)

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
        log_init_service()
        win32serviceutil.ServiceFramework.__init__(self, *args)
        logging.info('init')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.runflag = False

        from rpyc.utils.server import ThreadedServer
        # make sure only connections from localhost are accepted
        self.svc = ThreadedServer(RPCService, hostname = 'localhost', port = 18861)

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
        self.svc.start()
        self.runflag = True

        while self.runflag:
            self.sleep(10)
            logging.debug("Service is alive ...")

    # to be overridden
    def stop(self):
        logging.info("OVPN monitoring service shutting down...")
        self.svc.close()
        self.runflag = False
