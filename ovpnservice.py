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

def log(msg):
    #servicemanager.LogInfoMsg("SomeShortNameVersion - STOPPED!")
    print(msg)
    
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


OPENVPN_HOME = "../openvpn/"

class OVPNManagementThread(threading.Thread):
    def __init__(self):
        self.running = True
        self.connected = False
        self.sock = socket.socket()

    def terminate(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                if not self.connected:
                    self.sock.connect("localhost", 7505)

                self.check_status()
            except:
                log("Cannot connect to OVPN management socket")

            time.sleep(0.5)

    def check_status(self):
        self.sock.send("state")
        sleep(0.5)  # half a sec
        while 1:
            data = conn.recv(1024)
            if not data: 
                break
            else:
                resp = self.parse_status_response(data)

    def parse_status_response(self, msg):
        parts = string.split(msg, ",")
        pass

class OVPNService(rpyc.Service):
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.proc = None
        self.connected = False
        log("Connection from client opened...")

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
        path = os.path.join(current, OPENVPN_HOME)
        path = os.path.join(path, "openvpn")

        cfg = os.path.join(current, "..")
        cfg = os.path.join(cfg, "__config.ovpn")

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
        print("returned from subprocess call")
        ## test that service is runnig
        self.connected = True

    def exposed_ovpn_stop(self):
        self.proc.kill()


if __name__ == "__main__":
##    serv = OVPNService()
##    serv.exposed_start_ovpn()
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(OVPNService, port = 18861)
    log("OVPN service starting...")
    t.start()
