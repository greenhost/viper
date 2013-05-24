### Service to restart OpenVPN on windows
### (c) Luis Rodil-Fernandez <luis@greenhost.nl>
### Run Python scripts as a service example (ryrobes.com)
### Usage : python aservice.py install (or / then start, stop, remove)
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


##class aservice(win32serviceutil.ServiceFramework):
##   
##   _svc_name_ = "OVPNHandler"
##   _svc_display_name_ = "Greenhost OpenVPN Client Service"
##   _svc_description_ = "This service takes care of starting and shutting down the OpenVPN client"
##         
##   def __init__(self, args):
##           win32serviceutil.ServiceFramework.__init__(self, args)
##           self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)           
##
##   def SvcStop(self):
##           self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
##           win32event.SetEvent(self.hWaitStop)                    
##         
##   def SvcDoRun(self):
##      import servicemanager      
##      servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, '')) 
##      
##      #self.timeout = 640000    #640 seconds / 10 minutes (value is in milliseconds)
##      self.timeout = 120000     #120 seconds / 2 minutes
##      # This is how long the service will wait to run / refresh itself (see script below)
##
##      while 1:
##         # Wait for service stop signal, if I timeout, loop again
##         rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
##         # Check to see if self.hWaitStop happened
##         if rc == win32event.WAIT_OBJECT_0:
##            # Stop signal encountered
##            servicemanager.LogInfoMsg("SomeShortNameVersion - STOPPED!")  #For Event Log
##            break
##         else:
##
##                 #Ok, here's the real money shot right here.
##                 #[actual service code between rests]
##                 try:
##                     file_path = "C:\whereever\my_REAL_py_work_to_be_done.py"
##                     execfile(file_path)             #Execute the script
##                 except:
##                     pass
##                 #[actual service code between rests]
##
##
##def ctrlHandler(ctrlType):
##   return True
##                  
##if __name__ == '__main__':   
##   win32api.SetConsoleCtrlHandler(ctrlHandler, True)   
##   win32serviceutil.HandleCommandLine(aservice)
##
# Done! Lets go out and get some dinner, bitches!

# global that keeps track of the current status
OVPN_STATUS = None
stlock = threading.RLock()

class OVPNManagementThread(threading.Thread):
    def __init__(self):
        print "creating monitor thread..."
        self.running = True
        self.connected = False
        self.sock = None
        threading.Thread.__init__(self)

    def close(self):
        if self.connected:
            self.sock.shutdown(1)
            self.sock.close()
            self.connected = False


    def terminate(self):
        self.close()
        self.running = False

    def run(self):
        global OVPN_STATUS
        while self.running:
            try:
                if not self.connected:
                    self.sock = socket.socket()
                    self.sock.connect(("localhost", 7505))
                    self.connected = True

                self.check_status()
            except Exception, e:
                log("Cannot connect to OVPN management socket")
                OVPN_STATUS = {'status': "DISCONNECTED"} 
                self.close()
                print e

            if OVPN_STATUS: 
                st = OVPN_STATUS['status'] if 'status' in OVPN_STATUS else "undefined"
            else: 
                st = "undefined"
            print( st )
            time.sleep(0.5)

    def check_status(self):
        global OVPN_STATUS
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
        return self.connected

    def exposed_ovpn_start(self):
        current = os.getcwd()
        path = os.path.join(current, tools.get_openvpn_home())
        path = os.path.join(path, "openvpn")

        cfg = os.path.join(current, "__config.ovpn")

        ##import subprocess
        ##subprocess.call(['runas', '/user:Administrator', 'C:/my_program.exe'])

##        import win32api
##        win32api.ShellExecute( 0, # parent window
##            "runas", # need this to force UAC to act
##            "C:\\python27\\python.exe", 
##            "c:\\path\\to\\script.py", 
##            "C:\\python27", # base dir
##            1 ) # window visibility - 1: visible, 0: background

        cmd = "%s %s" % (path, cfg)
        print('Executing "' + cmd + '" as Administrator')
        #self.proc = subprocess.Popen(['runas', '/user:Administrator', cmd], shell=True, stdout=sys.stdout, stderr=sys.stdout)
        self.proc = subprocess.Popen([path, cfg], stdout=sys.stdout, stderr=sys.stdout)
        ## openvpn __config.ovpn
        #self.proc = subprocess.call([path, cfg], shell=True)
        # print("returned from subprocess call")
        # ## test that service is runnig
        # self.connected = True

    def exposed_ovpn_stop(self):
        self.proc.kill()


if __name__ == "__main__":
##    serv = OVPNService()
##    serv.exposed_start_ovpn()
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(OVPNService, port = 18861)
    log("OVPN service starting...")
    t.start()