#!/usr/bin/env python
import os, sys, re
import win32api
import win32con
import win32ui
import win32gui_struct
import win32file
import systray
import tools
from tools import log
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
service = None


##
## rpyc client to connect to windows service
##
class RemoteService:
    '''This service manager is meant to run on the same machine as the service itself, the localhost connection is hardcoded.
    '''
    def __init__(self, host="localhost", port=18861):
        self.connection = rpyc.connect(host, port)

    def connect(self):
        current = os.getcwd()
        cfg = os.path.join(current, "__config.ovpn")
        print "Loading config %s..." % (cfg,)
        r =  self.connection.root.ovpn_start(cfg)
        print r
        return r

    def disconnect(self):
        return self.connection.root.ovpn_stop()

    def is_connected(self):
        return self.connection.root.is_connected()

    def get_connection_settings():
        pass

    def get_gateway():
        pass

    def get_interface_ip():
        pass
    

class ConnectionMonitor(threading.Thread):
    def __init__(self):
        global service
        
        print "Creating thread to check connection status..."
        self.running = True
        self.connected = False

        # open connection to windows service to monitor status
        try:
            #win32api.MessageBox(0, "BOLLOCKS!", 'Service not running', 0x10)
            service = RemoteService(host="localhost", port=18861)
        except:
            win32api.MessageBox(0, "Seems like the OVPN service isn't running. Please run the OVPN service and then try running the umanager again. \n\nI will close when you press OK. Goodbye!", 'Service not running', 0x10)
            print("Please run the OVPN service to continue")
            sys.exit(1)

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
    
            
def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, str)


## ###########################################################################
## event handlers
## ###########################################################################
def vpn_browser_check(checkurl):
    import webbrowser
    webbrowser.open(checkurl)
    

def handle_configure(sysTrayIcon):
    print("Starting with configuration.")

    r = os.path.exists(config_file)
    if r:
        r = win32api.MessageBox(0, 'VPN already configured. Overwrite config?', 'Overwrite config', win32con.MB_YESNOCANCEL)
        if r == win32con.IDYES:
            dlg = win32ui.CreateFileDialog(1, None,None,
                                           (win32con.OFN_FILEMUSTEXIST|win32con.OFN_EXPLORER),
                                           'VPN configuration (*.ovpn)|*.ovpn||')
        else:
            return False

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
            r = os.path.exists(config_file)
            if r:
                try:
                    os.remove(config_file)
                except OSError:
                    show_message('Error removing old configuration', 'Error removing old configuration')
                    return False

            # Be sure old file is gone    
            r = os.path.exists(config_file)
            if r:
                show_message('Error removing old configuration', 'Error removing old configuration')
                return False

            # Ok, file is not there anymore, copy it        
            win32file.CopyFile(filename, config_file, 0);

            r = os.path.exists(config_file)
            if not r:
                show_message('Error coping config file', 'Error copying config file')
                return False
                

def show_message(message, title):
    win32api.MessageBox(0, message, title)
    
def handle_go_online(sysTrayIcon):
    global vpn_status, service
    
    # Check if config file exists
    r = os.path.exists(config_file)
    if not r:
        show_message('No configuration found. Unable to start VPN', 'No configuration found')
        return False

    if service.is_connected():
        show_message('VPN already active, cannot go online twice', 'Already online')
        return False

    # Open openvpn thru openvpn-control-daemon

    # Wait for reply and change icon. Give feedback?
    # Give feedback on failure
    
    # Enable some timer to check tunnel status every x minutes
    try:
        service.connect()
    except Exception, e:
        log("Service seems to be down")
        print e

    # Ok we are online now
    set_icon_online(sysTrayIcon)
    return True

def handle_go_offline(sysTrayIcon):
    global vpn_status, service

    if not service.is_connected():
        show_message('VPN not online, cannot go offline when offline', 'Already offline')
        return False

    # Disable timer for vpn check
    
    # Close openvpn thru openvpn-control-daemon
    # Wait for reply and change icon. Give feedback?
    try:
        service.disconnect()
    except Exception, e:
        log("Service seems to be down")
        print e
        
    
    set_icon_offline(sysTrayIcon)
    vpn_status = False
    return True

def set_icon_online(sysTrayIcon):
    sysTrayIcon.icon = icon_online
    sysTrayIcon.refresh_icon()

def set_icon_offline(sysTrayIcon):
    sysTrayIcon.icon = icon_offline
    sysTrayIcon.refresh_icon()

def handle_quit(sysTrayIcon):
    #handle_go_offline(sysTrayIcon)
    print('Bye, then.')

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


# def connect_to_service():
#     global service

#     try:
#         #win32api.MessageBox(0, "BOLLOCKS!", 'Service not running', 0x10)
#         service = RemoteService(host="localhost", port=18861)
#     except:
#         win32api.MessageBox(0, "Seems like the OVPN service isn't running. Please run the OVPN service and then try running the umanager again. \n\nI will close when you press OK. Goodbye!", 'Service not running', 0x10)
#         print("Please run the OVPN service to continue")
#         sys.exit(1)

# icons = itertools.cycle(glob.glob('*.ico'))
icon_online = 'online.ico'
icon_offline = 'offline.ico'
vpn_status = False
config_file = '__config.ovpn'
hover_text = "IWPR VPN: Not connected"

if __name__ == '__main__':
    import itertools, glob
    import shutil

    #win32api.MessageBox(0, "BOLLOCKS!", 'Service not running', 0x10)
    connect_to_service()

    checkurl = config_check_url(config_file)
    #print("URL to check VPN connection %s ..." % (checkurl,))


    menu_options = (('Configure ...', None, handle_configure, None),
                    
                    ('Go online ...', None, handle_go_online, None),
                    ('Go offline ...', None, handle_go_offline, win32con.MFS_DISABLED)
                   )
    
    systray.SysTrayIcon('offline.ico', hover_text, menu_options, on_quit=handle_quit, default_menu_index=1)

