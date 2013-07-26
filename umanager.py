#!/usr/bin/env python
import os, sys, re
import win32api
import win32con
import win32ui
import win32gui_struct
import win32file
import threading, time
from pprint import pprint

from win import routing 
from  win import systray
#import tools
from win.tools import *

# dependencies
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

try:
    import rpyc
except ImportError:
    print("RPYC module is required for interprocess communication. Please see: http://rpyc.readthedocs.org/en/latest/")


# globals
monitor = None
trayapp = None
svcproxy = None
config_file = '__config.ovpn'
hover_text = "IWPR VPN: Not connected"
checkurl = None

# icon_online = os.path.join(get_my_cwd(), 'online.ico')
# icon_offline = os.path.join(get_my_cwd(), 'offline.ico')
# icon_connecting = os.path.join(get_my_cwd(), 'connecting.ico')
# icon_refresh = os.path.join(get_my_cwd(), 'refresh.ico')

icon_online = 'online.ico'
icon_offline = 'offline.ico'
icon_connecting = 'connecting.ico'
icon_refresh = 'refresh.ico'


def feedback_online(sysTrayIcon):
    global icon_online
    sysTrayIcon.icon = icon_online
    sysTrayIcon.refresh_icon()

    menu_options = (('Configure...', None, handle_configure, win32con.MFS_DISABLED),
                    
                     ('Go online...', None, handle_go_online, win32con.MFS_DISABLED),
                     ('Go offline...', None, handle_go_offline, None),
                     #('Validate against server...', None, handle_validate_server, None)
                    )
    sysTrayIcon.set_menu(menu_options)

def feedback_offline(sysTrayIcon):
    global icon_offline
    sysTrayIcon.icon = icon_offline
    sysTrayIcon.refresh_icon()
    menu_options = (('Configure...', None, handle_configure, None),
                    
                     ('Go online...', None, handle_go_online, None),
                     ('Go offline...', None, handle_go_offline, win32con.MFS_DISABLED)
                    )
    sysTrayIcon.set_menu(menu_options)

    if trayapp:
        trayapp.set_hover_text("IWPR VPN: Not connected")


def feedback_connecting(sysTrayIcon):
    global icon_connecting, monitor
    monitor.isstarting = False
    sysTrayIcon.icon = icon_connecting
    sysTrayIcon.refresh_icon()

    menu_options = (('Configure...', None, handle_configure, win32con.MFS_DISABLED),
                    
                     ('Go online...', None, handle_go_online, win32con.MFS_DISABLED),
                     ('Go offline...', None, handle_go_offline, win32con.MFS_DISABLED)
                    )
    sysTrayIcon.set_menu(menu_options)


def feedback_starting(sysTrayIcon):
    global icon_refresh
    sysTrayIcon.icon = icon_refresh
    sysTrayIcon.refresh_icon()

    menu_options = (('Configure...', None, handle_configure, win32con.MFS_DISABLED),
                    
                     ('Go online...', None, handle_go_online, win32con.MFS_DISABLED),
                     ('Go offline...', None, handle_go_offline, win32con.MFS_DISABLED)
                    )
    sysTrayIcon.set_menu(menu_options)

def feedback_inconsistent(sysTrayIcon):
    global svcproxy
    win32api.MessageBox(0, "We have detected an inconsistency in the encryption of the connection\nit is therefore not secure to continue like this.\nThis can happen because sometimes windows becomes confused about the number of encrypted connections open.\n\nFor your security, I will stop the connection to the VPN now. Please try again after rebooting your windows computer.\n", 'Encryption status inconsistent', 0x10)

    try:
        svcproxy.disconnect()
    except Exception, e:
        log("Service seems to be down")
        print e


##
## rpyc client to connect to windows service
##
class ServiceProxy:
    '''This service manager is meant to run on the same machine as the service itself, the localhost connection is hardcoded.
    '''
    def __init__(self, host="localhost", port=18861):
        self.connection = rpyc.connect(host, port)

    def connect(self):
        #current = os.getcwd()
        cfg = os.path.join(get_user_cwd(), "__config.ovpn")
        log( "Loading config %s..." % (cfg,) )
        r =  self.connection.root.ovpn_start(cfg)
        return r

    def disconnect(self):
        log("umanager proxy - disconnect called")
        return self.connection.root.ovpn_stop()

    def is_connected(self):
        return self.connection.root.is_connected()

    def get_vpn_status(self):
        return self.connection.root.get_vpn_status()

    def get_connection_settings(self):
        return self.connection.root.get_connection_settings()

    def get_gateway_ip(self):
        return self.connection.root.get_gateway_ip()

    def get_interface_ip(self):
        return self.connection.root.get_interface_ip()
    

class ConnectionMonitor(threading.Thread):
    def __init__(self):
        global svcproxy

        self.running = True
        self.isstarting = False
        # open connection to windows service to monitor status
        try:
            #win32api.MessageBox(0, "BOLLOCKS!", 'Service not running', 0x10)
            svcproxy = ServiceProxy(host="localhost", port=18861)
        except:
            win32api.MessageBox(0, "Seems like the OVPN service isn't running. Please run the OVPN service and then try running the umanager again. \n\nI will close when you press OK. Goodbye!", 'Service not running', 0x10)
            print("Please run the OVPN service to continue")
            sys.exit(1)

        threading.Thread.__init__(self)

#    def close(self):
#        log("umanager.monitor - close called")
#        self.terminate()

    def terminate(self):
        log("umanager.monitor - terminate called")
        global svcproxy
        self.running = False
        svcproxy.disconnect()

    def run(self):
        global svcproxy, trayapp

        while self.running:
            try:
                #print("Monitoring... ")
                # openvpn is reporting back that we are online
                st = svcproxy.get_vpn_status()
                log("Status: %s" % st)
                if st == "CONNECTED":
                    if trayapp:
                        feedback_online(trayapp)
                elif st == "CONNECTING":
                    if trayapp: 
                        #print("connecting.........")
                        caption = "Connecting, please wait..."
                        trayapp.set_hover_text(caption)
                        feedback_connecting(trayapp)
                elif st == "INCONSISTENT":
                    if trayapp: 
                        feedback_inconsistent(trayapp)
                else:
                    # it's possible proxy has not yet started remote process
                    if self.isstarting:
                        feedback_starting(trayapp)
                    # proxy started the service but it is offline
                    else:
                        feedback_offline(trayapp)

                cs = svcproxy.get_connection_settings()
                if cs and trayapp: 
                    caption = "Connected to\ngateway: %s\nwith ip: %s\n" % (cs['gateway'], cs['interface'])
                    trayapp.set_hover_text(caption)
            except Exception, e:
                err = "umanager.monitor main loop: {0}".format(e.message)
                log(err)
                self.terminate()
                print e

            time.sleep(0.5)

    
def start_monitor():
    global monitor
    log("Creating thread to check connection status...")
    monitor = ConnectionMonitor()
    monitor.start()

def stop_monitor():
    global monitor
    log("Stopping thread that checks connection status...")
    monitor.terminate()

            
## ###########################################################################
## event handlers
## ###########################################################################
def vpn_browser_check(url):
    import webbrowser
    webbrowser.open(url)

def handle_validate_server(sysTrayIcon):
    vpn_browser_check(checkurl)
    return True

def handle_configure(sysTrayIcon):
    print("Starting with configuration.")

    cfgdst = os.path.join(get_user_cwd(), config_file)

    r = os.path.exists(cfgdst)
    if r:
        r = win32api.MessageBox(0, 'VPN already configured. Overwrite config?', 'Overwrite config', win32con.MB_YESNOCANCEL)
        if r != win32con.IDYES:
            return False

    dlg = win32ui.CreateFileDialog(1, None,None,
                                   (win32con.OFN_FILEMUSTEXIST|win32con.OFN_EXPLORER),
                                   'VPN configuration (*.ovpn)|*.ovpn||')
    dlg.SetOFNTitle('Select OpenVPN Files')
    testvalue = dlg.DoModal()
    if testvalue == win32con.IDOK:

            # Good reply, we have a file
            filename = dlg.GetPathNames()[0]
            e = os.path.exists(filename)
            if not e:
                show_message('Error opening file', 'Error opening file')
                return False

            # If old file exits, delete it
            r = os.path.exists(cfgdst)
            if r:
                try:
                    os.remove(cfgdst)
                except OSError:
                    show_message('Error removing old configuration', 'Error removing old configuration')
                    return False

            # Be sure old file is gone    
            r = os.path.exists(cfgdst)
            if r:
                show_message('Error removing old configuration', 'Error removing old configuration')
                return False

            # Ok, file is not there anymore, copy it        
            win32file.CopyFile(filename, cfgdst, 0);

            r = os.path.exists(cfgdst)
            if not r:
                show_message('Error copying config file', 'Error copying config file')
                return False
                

def show_message(message, title):
    win32api.MessageBox(0, message, title)
    
def handle_go_online(sysTrayIcon):
    global svcproxy, monitor
    
    # Check if config file exists
    r = os.path.exists(os.path.join(get_user_cwd(), config_file))
    if not r:
        show_message('No configuration found. Unable to start VPN', 'No configuration found')
        return False

    if not svcproxy:
        log("SVCProxy is not properly initialized (probably disconnected)")

    if svcproxy.is_connected():
        show_message('VPN already active, cannot go online twice', 'Already online')
        return False

    try:
        svcproxy.connect()
        # show immediate feedback to the user
        monitor.isstarting = True
    except Exception, e:
        log("Service seems to be down")
        print e

    return True

def handle_go_offline(sysTrayIcon):
    global svcproxy

    if not svcproxy.is_connected():
        show_message('VPN not online, cannot go offline when offline', 'Already offline')
        return False

    try:
        svcproxy.disconnect()
    except Exception, e:
        log("Service seems to be down")
        print e
        
    return True

def handle_quit(sysTrayIcon):
    # stop monitoring
    stop_monitor()
    log('Bye, then.')
    #os._exit(os.EX_OK)

def config_check_url(cfgfile):
    try:
       with open(cfgfile, "r") as f:
            pattern = re.compile("check-url (\S+)")
            for line in f:
                if "check-url" in line:
                    matches = pattern.findall(line)
                    if matches:
                        return matches[0]
                    else:
                        continue
                else:
                    continue

    except IOError:
        log("Couldn't open config file to search for Check URL")

    return None



if __name__ == '__main__':
    import itertools, glob
    import shutil

    #win32api.MessageBox(0, "CWD: %s\nOPENVPN_HOME: %s\sys.executable: %s" % (os.getcwd(),get_openvpn_home(), ) , 'Debug', 0x10)

    start_monitor()

    #checkurl = config_check_url(config_file)
    #print("URL to check VPN connection %s ..." % (checkurl,))


    menu_options = (('Configure ...', None, handle_configure, None),
                    
                    ('Go online ...', None, handle_go_online, None),
                    ('Go offline ...', None, handle_go_offline, win32con.MFS_DISABLED)
                   )
    
    trayapp = systray.SysTrayIcon(icon_offline, hover_text, menu_options, on_quit=handle_quit, default_menu_index=1)
    # !!! must call the loop function to enter the win32 message pump
    trayapp.loop()
