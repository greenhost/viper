#!/usr/bin/env python
""" 
Service to manage and monitor OpenVPN on windows
(c) Luis Rodil-Fernandez <luis@greenhost.nl>

Run Python scripts as a service example (ryrobes.com)
Usage : python aservice.py install (or / then start, stop, remove)
"""
import rpyc
import subprocess
import os, sys
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

from win import routing
#from win import tools
from win.tools import *
import traceback


# global that keeps track of the current status
OVPN_STATUS = None
# stlock = threading.RLock()

# class OVPNManagementThread(threading.Thread):
#     def __init__(self):
#         log("service - creating monitor thread...")
#         self.running = True
#         self.connected = False
#         #self.sock = None #socket.socket()
#         #self.sock.settimeout(5)
#         self.delaytime = 0.5
#         self.conntimeout = 2
#         #self.tstamp_started_check = None
#         #self.tstamp_check_timeout = 5
#         threading.Thread.__init__(self)

#     def close(self):
#         """ close OpenVPN client sending SIGTERM """
#         log("Terminating OpenVPN subprocess [SIGTERM]")

#         # terminate openvpn processes
#         procs = tools.is_openvpn_running()
#         if procs: # process found, terminate it
#             for p in procs:
#                 p.terminate()

#     def terminate(self):
#         """ stop monitoring """
#         try:
#             self.close()
#         except Exception, e:
#             log("Couldn't terminate openvpn processes for some unknown reason: %s" % e)
#         finally:
#             # make sure thread loop stops checking
#             self.running = False

#     def run(self):
#         global OVPN_STATUS
#         log("Thread is running...")
#         while self.running:

#             sock = socket.socket()
#             try:
#                 #if not self.connected:
#                 log("Trying to connect to OVPN management socket")
#                 sock.settimeout( self.conntimeout )
#                 sock.connect(("localhost", 7505))
#                 # self.sock.setblocking(1)
#                 self.connected = True

#                 log("Connected successfully to management socket")

#                 self.check_status(sock)
#             except socket.timeout, e:
#                 log("OVPN management socket operation timed-out: %s" % e)
#                 OVPN_STATUS = {'status': "DISCONNECTED"} 
#             except Exception, e:
#                 log("OVPN management socket error: %s" % e)
#                 OVPN_STATUS = {'status': "DISCONNECTED"} 
#             finally:   # always execute
#                 try:
#                     sock.close()
#                     self.connected = False
#                     del sock
#                     #time.sleep(5)
#                 except Exception, e:
#                     log("FATAL - closing the socket failed the next open operation would not work")
#                     raise


#             # if OVPN_STATUS: 
#             #     st = OVPN_STATUS['status'] if 'status' in OVPN_STATUS else "undefined"
#             # else: 
#             #     st = "undefined"
        
#         log("Exiting monitor thread main loop")




class RPCService(rpyc.Service):
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.proc = None
        #self.monitor = None
        self.connected = False
        log("Connection from client opened...")

        # # start monitor thread
        # try:
        #     self.monitor = OVPNManagementThread()
        #     log(">>> Trying to start thread...")
        #     self.monitor.start()
        # except Exception, e:
        #     log("Failed to start thread %s" % e)

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        log("Connection from client closed")

    def exposed_heartbeat(self):
        return str(datetime.now())

    def exposed_is_connected(self):
        global OVPN_STATUS
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return True
        else:
            return False

    def exposed_get_vpn_status(self):
        global OVPN_STATUS
        if OVPN_STATUS:
            return OVPN_STATUS['status']
        else:
            return None

    def exposed_get_connection_settings(self):
        global OVPN_STATUS
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS
        else:
            return None

    def exposed_get_gateway_ip(self):
        global OVPN_STATUS
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS['gateway']
        else:
            return None

    def exposed_get_interface_ip(self):
        global OVPN_STATUS
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS['interface']
        else:
            return None

    def exposed_ovpn_start(self, cfgfile):
        global OVPN_STATUS
        log("Start on manager thread called, ready to call OpenVPN")
        path = get_openvpn_home()
        path = os.path.join(path, "openvpn")

        cmd = "%s %s" % (path, cfgfile)
        log("Trying to execute OpenVPN client %s" % (cmd,))
        f = open(os.devnull, 'w')

        self.proc = subprocess.Popen([path, cfgfile], stdout=f, stderr=f)

    def exposed_ovpn_stop(self):
        global OVPN_STATUS
        #self.monitor.terminate()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(RPCService, port = 18861)
    log("OVPN service starting...")
    t.start()
