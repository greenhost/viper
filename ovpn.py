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

import routingtools
import tools
from tools import log
import traceback


# global that keeps track of the current status
OVPN_STATUS = None
stlock = threading.RLock()

class OVPNManagementThread(threading.Thread):
    def __init__(self):
        log("service - creating monitor thread...")
        self.running = True
        self.connected = False
        #self.sock = socket.socket()
        #self.sock.settimeout(5)
        self.delaytime = 0.5
        #self.tstamp_started_check = None
        #self.tstamp_check_timeout = 5
        threading.Thread.__init__(self)

    def disconnect(self):
        """ disconnect monitoring thread from OpenVPN client """
        #if self.connected:
        #    # close the socket
        #    self.sock.shutdown(socket.SHUT_RDWR)
        try:
            self.sock.close()
            self.connected = False
            del self.sock
        except Exception, e:
            log("FATAL - closing the socket failed the next open operation would not work")
            raise

    def close(self):
        """ close OpenVPN client sending SIGTERM """
        log("Terminating OpenVPN subprocess [SIGTERM]")
        # send SIGTERM to openvpn
        self.sock.send("signal SIGTERM\n")

    def terminate(self):
        """ stop monitoring """
        self.close()
        self.disconnect()
        self.running = False

    def run(self):
        global OVPN_STATUS
        while self.running:
            try:
                #if not self.connected:
                log("Trying to connect to OVPN management socket")

                self.sock = socket.socket()
                self.sock.settimeout(self.delaytime)
                self.sock.connect(("localhost", 7505))
                # self.sock.setblocking(1)
                self.connected = True

                log("Connected successfully to management socket")

                self.check_status()
            except socket.timeout:
                log("OVPN management socket operation timed-out")
                OVPN_STATUS = {'status': "DISCONNECTED"} 
            except Exception, e:
                log("OVPN management socket error: %s" % e)
                OVPN_STATUS = {'status': "DISCONNECTED"} 
            finally:   # always execute
                ##self.sock.shutdown(socket.SHUT_RDWR)
                #print("-"*60)
                #pprint(OVPN_STATUS)
                #print("-"*60)
                self.disconnect()


            if OVPN_STATUS: 
                st = OVPN_STATUS['status'] if 'status' in OVPN_STATUS else "undefined"
            else: 
                st = "undefined"
        
        log("Exiting monitor thread main loop")

    def verify_connection(self, stats):
            # verify that the routing table matches status readings
            if ( ('status' in stats) 
                and (stats['status'] == 'CONNECTED') 
                and ('gateway' in stats) ):
                if routingtools.verify_vpn_routing_table( stats['gateway'] ):
                    return True

            else:
                return False


    def check_status(self):
        global OVPN_STATUS
        #log("Checking status")
        self.sock.makefile()
        self.sock.send("state\n")
        time.sleep(self.delaytime) # must wait a bit otherwise we will not get a response to our request

        data = self.sock.recv(1024)

        if not data:
            OVPN_STATUS = {'status': "DISCONNECTED"} 
        else:
            log("RECV raw: %s" % (data,) )
            resp = self.parse_status_response(data)
            #pprint(OVPN_STATUS)
            # compare status with routing table
            with stlock:
                OVPN_STATUS = resp
                #log( "State command response: %s" % (OVPN_STATUS['status'],) )

            # verify that the routing table matches status readings
            try:
                if (not OVPN_STATUS or self.verify_connection(OVPN_STATUS)):
                    OVPN_STATUS = {'status' : "DISCONNECTED"}
            except routingtools.InconsistentRoutingTable:
                OVPN_STATUS = {'status' : "INCONSISTENT"}


    def parse_status_response(self, msg):
        """ Parse messages like this: 
                >INFO:OpenVPN Management Interface Version 1 -- type 'help' for more info
                1374575393,CONNECTED,SUCCESS,172.26.37.6,213.108.105.101
                END
        """
        try:
            lines = string.split(msg, os.linesep)

            if(len(lines) > 2):
                parts = string.split(lines[1], ",")

                # get line containing status
                if parts[1] == "CONNECTED" and parts[2] == "SUCCESS":
                    return {'status': "CONNECTED", 'interface' : parts[4].split('\r')[0], 'gateway' : parts[3]}
                elif parts[1] == "ASSIGN_IP":
                    return {'status': "CONNECTING"}

            else:
                return None
        except Exception, e:
            log("Failed to parse status response: %s" % e)


class OVPNService(rpyc.Service):
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.proc = None
        self.monitor = None
        self.connected = False
        log("Connection from client opened...")

        # start monitor thread
        self.monitor = OVPNManagementThread()
        self.monitor.start()

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        log("Connection from client closed")

    def exposed_heartbeat(self):
        return str(datetime.now())

    def exposed_is_connected(self):
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return True
        else:
            return False

    def exposed_get_vpn_status(self):
        if OVPN_STATUS:
            return OVPN_STATUS['status']
        else:
            return None

    def exposed_get_connection_settings(self):
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS
        else:
            return None

    def exposed_get_gateway_ip(self):
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS['gateway']
        else:
            return None

    def exposed_get_interface_ip(self):
        if OVPN_STATUS and OVPN_STATUS['status'] == "CONNECTED":
            return OVPN_STATUS['interface']
        else:
            return None

    def exposed_ovpn_start(self, cfgfile):
        log("Start on manager thread called, ready to call OpenVPN")
        path = tools.get_openvpn_home()
        path = os.path.join(path, "openvpn")

        #cfg = os.path.join(current, "__config.ovpn")

        ##import subprocess
        ##subprocess.call(['runas', '/user:Administrator', 'C:/my_program.exe'])

##        import win32api
##        win32api.ShellExecute( 0, # parent window
##            "runas", # need this to force UAC to act
##            "C:\\python27\\python.exe", 
##            "c:\\path\\to\\script.py", 
##            "C:\\python27", # base dir
##            1 ) # window visibility - 1: visible, 0: background

        cmd = "%s %s" % (path, cfgfile)
        log("Trying to execute OpenVPN client %s" % (cmd,))
        f = open(os.devnull, 'w')
        #self.proc = subprocess.Popen(['runas', '/user:Administrator', cmd], shell=True, stdout=f, stderr=f)
        #return 'Executing "' + cmd + '" as Administrator'
        self.proc = subprocess.Popen([path, cfgfile], stdout=f, stderr=f)
        ## openvpn __config.ovpn
        #self.proc = subprocess.call([path, cfg], shell=True)
        # print("returned from subprocess call")
        # ## test that service is runnig
        # self.connected = True

    def exposed_ovpn_stop(self):
        if self.proc: 
            self.monitor.close()
            self.monitor.disconnect()
            #self.proc.kill()


if __name__ == "__main__":
##    serv = OVPNService()
##    serv.exposed_start_ovpn()
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(OVPNService, port = 18861)
    log("OVPN service starting...")
    t.start()
