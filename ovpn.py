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
        log("service - ctor line 1")
        self.running = True
        log("service - ctor line 2")
        self.connected = False
        log("service - ctor line 3")
        #self.sock = None #socket.socket()
        #self.sock.settimeout(5)
        self.delaytime = 0.5
        log("service - ctor line 4")
        #self.tstamp_started_check = None
        #self.tstamp_check_timeout = 5
        threading.Thread.__init__(self)

    def close(self):
        """ close OpenVPN client sending SIGTERM """
        log("Terminating OpenVPN subprocess [SIGTERM]")
        # send SIGTERM to openvpn
        sock = socket.socket()
        try:
            sock.settimeout(self.delaytime)
            sock.connect(("localhost", 7505))
            # self.sock.setblocking(1)
            connected = True
            sock.send("signal SIGTERM\n")
        except Exception, e:
            log("Couldn't send terminate signal to OpenVPN process: %s" % e)
        finally:
            sock.close()
            self.connected = False
            del sock

    def terminate(self):
        """ stop monitoring """
        self.close()
        self.running = False

    def run(self):
        global OVPN_STATUS
        log("Thread is running...")
        while self.running:

            sock = socket.socket()
            try:
                #if not self.connected:
                log("Trying to connect to OVPN management socket")
                sock.settimeout(self.delaytime)
                sock.connect(("localhost", 7505))
                # self.sock.setblocking(1)
                self.connected = True

                log("Connected successfully to management socket")

                self.check_status(sock)
            except socket.timeout:
                log("OVPN management socket operation timed-out")
                OVPN_STATUS = {'status': "DISCONNECTED"} 
            except Exception, e:
                log("OVPN management socket error: %s" % e)
                OVPN_STATUS = {'status': "DISCONNECTED"} 
            finally:   # always execute
                try:
                    sock.close()
                    self.connected = False
                    del sock
                except Exception, e:
                    log("FATAL - closing the socket failed the next open operation would not work")
                    raise


            # if OVPN_STATUS: 
            #     st = OVPN_STATUS['status'] if 'status' in OVPN_STATUS else "undefined"
            # else: 
            #     st = "undefined"
        
        log("Exiting monitor thread main loop")


    def check_status(self, socket):
        global OVPN_STATUS
        #log("Checking status")
        socket.send("state\n")
        time.sleep(self.delaytime) # must wait a bit otherwise we will not get a response to our request

        data = socket.recv(1024)

        if not data:
            OVPN_STATUS = {'status': "DISCONNECTED"} 
            log("No data received while reading socket")
        else:
            log("RECV raw: %s" % (data,) )
            resp = self.parse_status_response(data)
            #pprint(OVPN_STATUS)
            # compare status with routing table
            if resp:
                OVPN_STATUS = resp

                # verify that the routing table matches status readings
                if OVPN_STATUS['status'] == "CONNECTED":
                    try:
                        if not routingtools.verify_vpn_routing_table(OVPN_STATUS['gateway']):
                            OVPN_STATUS = {'status' : "DISCONNECTED"}
                            log("Routing verification didn't pass")
                    except routingtools.InconsistentRoutingTable:
                        OVPN_STATUS = {'status' : "INCONSISTENT"}
                        log("Routing verification is not consistent")

            else:
                OVPN_STATUS = {'status' : "DISCONNECTED"}
                #log( "State command response: %s" % (OVPN_STATUS['status'],) )


    def parse_status_response(self, msg):
        """ Parse messages like this: 
                >INFO:OpenVPN Management Interface Version 1 -- type 'help' for more info
                1374575393,CONNECTED,SUCCESS,172.26.37.6,213.108.105.101
                END
        """
        try:
            lines = string.split(msg, os.linesep)

            for l in lines:
                if ',' in l:
                    parts = string.split(l, ",")

                    # get line containing status
                    if parts[1] == "CONNECTED" and parts[2] == "SUCCESS":
                        return {'status': "CONNECTED", 'interface' : parts[4].split('\r')[0], 'gateway' : parts[3]}
                    elif parts[1] == "ASSIGN_IP":
                        return {'status': "CONNECTING"}
                    else:
                        return None
                else:
                    continue
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
        try:
            self.monitor = OVPNManagementThread()
            log(">>> Trying to start thread...")
            self.monitor.start()
        except Exception, e:
            log("Failed to start thread %s" % e)

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
        global OVPN_STATUS
        self.monitor.terminate()

        # if self.proc: 
        #     self.monitor.close()
        #     self.monitor.disconnect()
            #self.proc.kill()


if __name__ == "__main__":
##    serv = OVPNService()
##    serv.exposed_start_ovpn()
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(OVPNService, port = 18861)
    log("OVPN service starting...")
    t.start()
