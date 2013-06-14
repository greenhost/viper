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
import tools
from pprint import pprint
from tools import log



# global that keeps track of the current status
OVPN_STATUS = None
stlock = threading.RLock()

class OVPNManagementThread(threading.Thread):
    def __init__(self):
        log("service - creating monitor thread...")
        self.running = True
        self.connected = False
        self.sock = None
        threading.Thread.__init__(self)

    def disconnect(self):
        """ disconnect monitoring thread from OpenVPN client """
        if self.connected:
            # close the socket
            self.sock.shutdown(1)
            self.sock.close()
            self.connected = False

    def close(self):
        """ close OpenVPN client sending SIGTERM """
        log("Terminating OpenVPN subprocess [SIGTERM]")
        # send SIGTERM to openvpn
        self.sock.send("signal SIGTERM\n")
        time.sleep(0.5)  # half a sec

    def terminate(self):
        """ stop monitoring """
        self.close()
        self.disconnect()
        self.running = False

    def run(self):
        global OVPN_STATUS
        while self.running:
            try:
                if not self.connected:
                    log("Trying to connect to OVPN management socket")
                    self.sock = socket.socket()
                    self.sock.connect(("localhost", 7505))
                    self.connected = True

                self.check_status()
            except Exception, e:
                log("Cannot connect to OVPN management socket")
                OVPN_STATUS = {'status': "DISCONNECTED"} 
                self.disconnect()
                print e

            if OVPN_STATUS: 
                st = OVPN_STATUS['status'] if 'status' in OVPN_STATUS else "undefined"
            else: 
                st = "undefined"
            print( st )
            time.sleep(0.5)

    def check_status(self):
        global OVPN_STATUS
        log("Checking status")
        self.sock.send("state\n")
        time.sleep(0.5)  # half a sec
        while 1:
            data = self.sock.recv(1024)
            if not data:
                OVPN_STATUS = {'status': "DISCONNECTED"} 
                break
            else:
                resp = self.parse_status_response(data)
                #pprint(OVPN_STATUS)
                with stlock:
                    OVPN_STATUS = resp
                break

    def parse_status_response(self, msg):
        """ Parse messages like this: 1369378632,CONNECTED,SUCCESS,10.20.2.14,171.33.130.90 """
        parts = string.split(msg, ",")
        if parts[1] == "CONNECTED" and parts[2] == "SUCCESS":
            return {'status': "CONNECTED", 'interface' : parts[3], 'gateway' : parts[4].split('\r')[0]}
        elif parts[1] == "ASSIGN_IP":
            return {'status': "CONNECTING"}


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
