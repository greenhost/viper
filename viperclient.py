#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Greenhost VOF
# https://greenhost.nl -\- https://greenhost.io
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os, sys, re
import win32api
import win32con
import win32ui
import win32gui_struct
import win32file
import threading, time, traceback
from pprint import pprint
import logging
import getopt
import atexit

import gettext
from gettext import gettext as _
gettext.install('messages', '../i18n', unicode=True)

import viper
from viper import routing 
from viper.openvpn import launcher, management
from viper.tools import *
from viper.windows import systray, balloon, firewall

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
hover_text = _("Not connected to VPN")
checkurl = None
debug_level = logging.DEBUG
quitting = False
user_wants_online = False  # keep this status to represent the intention of the user irrespective of what OpenVPN

def window_handle():
    """ get the window handle for the systray appplication if one exists """
    if trayapp and trayapp.hwnd:
        return trayapp.hwnd
    else:
        return 0

def feedback_online(sysTrayIcon):
    if sysTrayIcon and not quitting:
        sysTrayIcon.icon = viper.ICONS['online']
        sysTrayIcon.refresh_icon()

        menu_options = (( _('Configure...'), None, handle_configure, win32con.MFS_DISABLED),
                        
                         (_('Go online...'), None, handle_go_online, win32con.MFS_DISABLED),
                         (_('Go offline...'), None, handle_go_offline, None),
                         (_('Validate against server...'), None, handle_validate_server, None)
                        )
        sysTrayIcon.set_menu(menu_options)

def feedback_offline(sysTrayIcon):
    global trayapp
    if sysTrayIcon and not quitting:
        sysTrayIcon.icon = viper.ICONS['offline']
        sysTrayIcon.refresh_icon()
        menu_options = ((_('Configure...'), None, handle_configure, None),
                        
                         (_('Go online...'), None, handle_go_online, None),
                         (_('Go offline...'), None, handle_go_offline, win32con.MFS_DISABLED)
                         (_('Validate against server...'), None, handle_validate_server, None)
                        )
        sysTrayIcon.set_menu(menu_options)

        if trayapp:
            trayapp.set_hover_text(_("Not connected to VPN"))


def feedback_connecting(sysTrayIcon):
    global monitor
    if sysTrayIcon and not quitting:
        sysTrayIcon.icon = viper.ICONS['connecting']
        monitor.isstarting = False
        sysTrayIcon.refresh_icon()

        menu_options = ((_('Configure...'), None, handle_configure, win32con.MFS_DISABLED),
                        
                         (_('Go online...'), None, handle_go_online, win32con.MFS_DISABLED),
                         (_('Go offline...'), None, handle_go_offline, win32con.MFS_DISABLED)
                         (_('Validate against server...'), None, handle_validate_server, None)
                        )
        sysTrayIcon.set_menu(menu_options)


def feedback_starting(sysTrayIcon):
    if sysTrayIcon and not quitting:
        sysTrayIcon.icon = viper.ICONS['refresh']
        sysTrayIcon.refresh_icon()

        menu_options = ((_('Configure...'), None, handle_configure, win32con.MFS_DISABLED),
                        
                         (_('Go online...'), None, handle_go_online, win32con.MFS_DISABLED),
                         (_('Go offline...'), None, handle_go_offline, win32con.MFS_DISABLED)
                        )
        sysTrayIcon.set_menu(menu_options)

def feedback_inconsistent(sysTrayIcon):
    global svcproxy
    win32api.MessageBox(window_handle(), _("We have detected an inconsistency in routing of the traffic\nit is therefore not secure to continue like this.\nThis can happen because sometimes windows becomes confused about the number of encrypted connections open.\n\nFor your security, I will stop now. Please try again after rebooting your windows computer.\n"), _('Traffic routing inconsistent'), 0x10)

    try:
        svcproxy.disconnect()
    except Exception, e:
        logging.critical("Service seems to be down")
        print e


##
## rpyc client to connect to windows service
##
class ServiceProxy:
    '''Proxy the start/stop procedures for the connection stack through a Windows service and monitor
    the status of the conneciton subsequently. To run the stack with elevated privileges the windows service is
    required. Checking for status however can be done without elevated privileges.

    This service manager is meant to run on the same machine as the service itself, the localhost connection is hardcoded.
    '''
    def __init__(self, host="localhost", port=18861):
        """Initialize the local-link connection to the Widows service"""
        self.connection = rpyc.connect(host, port)
        self.ovpn = management.OVPNInterface()

    def connect(self):
        # start monitoring the management interface
        cfg = os.path.join(get_user_cwd(), "__config.ovpn")
        logging.info( "Trying to connect with config {0}...".format(cfg) )
        r = None
        try:
            r =  self.connection.root.ovpn_start(cfg, get_user_cwd())
        except Exception, e: # launcher.VPNLauncherException
            win32api.MessageBox(window_handle(), _("I failed to connect to the VPN, this might be due to a bad configuration file. Please get a fresh configuration file and try again or consult with your service provider."), _('Failed to run OpenVPN'), 0x10)
            logging.critical("Failed to run OpenVPN, reason: {0}".format(e.message))
            return False

        return r

    def disconnect(self):
        logging.info("proxy - disconnect called")
        return self.connection.root.ovpn_stop()

    def is_connected(self):
        return (self.get_vpn_status() == "CONNECTED")

    def get_vpn_status(self):
        status = self.ovpn.poll_status()
        return status['viper_status'] # if 'viper_status' in status else None

    def firewall_up(self):
        self.connection.root.firewall_up()

    def firewall_down(self):
        self.connection.root.firewall_down()

    def set_default_gateway(self, gwip):
        self.connection.root.set_default_gateway(gwip)

    def get_connection_settings(self):
        status = self.ovpn.poll_status()
        logging.debug(status)
        if status and status['viper_status'] == "CONNECTED":
            return status
        else:
            return None

    def get_gateway_ip(self):
        settings = self.get_connection_settings()
        return settings['gateway'] if 'gateway' in settings else None

    def get_interface_ip(self):
        settings = self.get_connection_settings()
        return settings['interface'] if 'interface' in settings else None

    def hangup(self):
        """ Send a running instance of openvpn a hangup signal so that it attempts 
            to reconfigure the connection stack 
        """
        self.ovpn.hangup()
    

class ConnectionMonitor(threading.Thread):
    def __init__(self):
        global svcproxy

        self.running = True
        self.isstarting = False
        self.state = None
        self.last_state = None
        # open connection to windows service to monitor status
        try:
            #win32api.MessageBox(0, "LOOKATME!", 'Service not running', 0x10)
            svcproxy = ServiceProxy(host="localhost", port=18861)
        except Exception, e:
            logging.warning("Failed to start the proxy to talk to the service: {0}".format( traceback.format_exc() ))
            win32api.MessageBox(window_handle(), _("Seems like the OVPN service isn't running. Please run the OVPN service and then try running the viper client again. \n\nI will close when you press OK. Goodbye!"), _('Service not running'), 0x10)
            #print("Please run the OVPN service to continue")
            sys.exit(1)

        threading.Thread.__init__(self)

#    def close(self):
#        log("viper - close called")
#        self.terminate()

    def terminate(self):
        logging.debug("viper - terminate called")
        global svcproxy
        self.running = False
        svcproxy.disconnect()

    def run(self):
        global svcproxy, trayapp, user_wants_online

        while self.running:
            try:
                #print("Monitoring... ")
                # openvpn is reporting back that we are online
                self.last_state = self.state
                self.state = svcproxy.get_vpn_status()
                logging.debug("Status: %s" % self.state)

                # immediately report it with a popup when the connection is lost
                if ( (self.last_state == "CONNECTED") and (self.state == "DISCONNECTED") ):
                    feedback_offline(trayapp)
                    if user_wants_online:
                        r = win32api.MessageBox(window_handle(), _('Your connection has dropped. You are now offline. Would you like to try reconnecting?'), _('Connection dropped'), win32con.MB_YESNO | win32con.MB_SYSTEMMODAL)
                        if r == win32con.IDYES:
                            logging.debug("User requested a reconnect, trying to send hangup signal to stack")
                            svcproxy.hangup()
                    # # @todo use a blocking dialog a balloon is completely innapropriate
                    # balloon.balloon_tip("Secure connection lost!", "The connection to the VPN has dropped, your communications are no longer protected. \n\nRestart Viper to secure your connection again.")

                # allow the client to time out for a few retries, keep reporting previous state
                if self.state == "TIMED-OUT":
                    self.state = self.last_state

                # report state on the systray
                if self.state == "CONNECTED":
                    if trayapp:
                        feedback_online(trayapp)
                elif self.state == "CONNECTING":
                    if trayapp: 
                        #print("connecting.........")
                        caption = _("Connecting, please wait...")
                        trayapp.set_hover_text(caption)
                        feedback_connecting(trayapp)
                elif self.state == "INCONSISTENT":
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
                    caption = _("Connected to the internet with ip: {0}\n").format(cs['gateway'])
                    trayapp.set_hover_text(caption)
            except Exception as e:
                feedback_offline(trayapp)
                err = "viper main loop: {0}".format( traceback.format_exc() )
                logging.critical(err)
                #caption = _("Not connected to the VPN")
                #trayapp.set_hover_text(caption)
                #self.terminate()
                print e

            time.sleep(0.5)

    
def start_monitor():
    global monitor
    logging.info("Creating thread to check connection status...")
    monitor = ConnectionMonitor()
    monitor.start()

def stop_monitor():
    global monitor
    logging.info("Stopping thread that checks connection status...")
    monitor.terminate()

            
## ###########################################################################
## event handlers
## ###########################################################################
def vpn_browser_check(url):
    import webbrowser
    webbrowser.open(url)

def handle_validate_server(sysTrayIcon):
    from viper.provider import *
    url = provider.get('landing-page')
    logging.debug("Validating connection against landing page {0}".format(url))
    vpn_browser_check( url )
    return True

def handle_configure(sysTrayIcon):
    logging.info("Starting with configuration.")

    cfgdst = os.path.join(get_user_cwd(), config_file)

    r = os.path.exists(cfgdst)
    if r:
        r = win32api.MessageBox(window_handle(), _('VPN already configured. Overwrite config?'), _('Overwrite config'), win32con.MB_YESNOCANCEL | win32con.MB_SYSTEMMODAL)
        if r != win32con.IDYES:
            return False

    dlg = win32ui.CreateFileDialog(1, None,None,
                                   (win32con.OFN_FILEMUSTEXIST|win32con.OFN_EXPLORER),
                                   _('VPN configuration (*.ovpn)|*.ovpn||'))
    dlg.SetOFNTitle(_('Select OpenVPN Files'))
    testvalue = dlg.DoModal()
    if testvalue == win32con.IDOK:

            # Good reply, we have a file
            filename = dlg.GetPathNames()[0]
            e = os.path.exists(filename)
            if not e:
                show_message(_('Error opening file'), _('Error opening file'))
                return False

            # If old file exits, delete it
            r = os.path.exists(cfgdst)
            if r:
                try:
                    os.remove(cfgdst)
                except OSError:
                    show_message(_('Error removing old configuration'), _('Error removing old configuration'))
                    return False

            # Be sure old file is gone    
            r = os.path.exists(cfgdst)
            if r:
                show_message(_('Error removing old configuration'), _('Error removing old configuration'))
                return False

            # Ok, file is not there anymore, copy it        
            win32file.CopyFile(filename, cfgdst, 0);

            r = os.path.exists(cfgdst)
            if not r:
                show_message(_('Error copying config file'), _('Error copying config file'))
                return False
                

def show_message(message, title):
    win32api.MessageBox(window_handle(), message, title)

def config_exists():
    return os.path.exists(os.path.join(get_user_cwd(), config_file))

def handle_go_online(sysTrayIcon):
    global svcproxy, monitor, user_wants_online

    # user has explicitly indicate that she wants to go online
    user_wants_online = True

    # flushing the dns cache doesn't harm and it can prevent dns leaks
    # @NOTE should we flush before connection is completed or should be flush only after new DNS
    # entries are injected by OpenVPN?
    flush_dns()

    # @todo save default gateway onto user dir
    tools.save_default_gateway()

    # if Windows Firewall is not enabled, refuse to connect
    if not firewall.is_firewall_enabled():
        logging.warning("Firewall is not enabled. I will not connect.")
        win32api.MessageBox(window_handle(), _("I see that Windows Firewall is not enabled. Viper needs it to safeguard your connection, so I will not connect now. Please enabled Windows Firewall in your machine and try connecting through Viper again."), _('Windows Firewall is disabled'), 0x30)
        return False
        
    # Check if config file exists
    if not config_exists():
        show_message(_('No configuration found. Unable to start VPN'), _('No configuration found'))
        return False

    if not svcproxy:
        logging.error("SVCProxy is not properly initialized (probably disconnected)")

    if svcproxy.is_connected():
        show_message(_('VPN already active, cannot go online twice'), _('Already online'))
        return False

    try:
        if svcproxy.connect():
            # show immediate feedback to the user
            monitor.isstarting = True
    except Exception, e:
        logging.critical("Service seems to be down")
        print e

    try:
        svcproxy.firewall_up()
    except Exception as e:
        err = "error setting up the firewall: {0}".format( traceback.format_exc() )
        logging.error(err)

    return True

def handle_go_offline(sysTrayIcon):
    global svcproxy, monitor, user_wants_online

    # user has explicitly indicate that she wants to be offline
    user_wants_online = False

    monitor.isstarting = False
    # connected = svcproxy.is_connected()
    # if not connected:
    #     show_message(_("VPN not online, cannot go offline when offline, is connected: {0}".format(connected) ), _('Already offline'))
    #     return False

    try:
        svcproxy.disconnect()
    except Exception, e:
        logging.critical("Service seems to be down")
        print e
        
    try:
        svcproxy.firewall_down()
    except Exception as e:
        err = "error tearing down the firewall: {0}".format( traceback.format_exc() )
        logging.error(err)

    # restore default gateway
    try:
        gwip = tools.recover_default_gateway()
        # only the service running with elevated privileges can insert the default route
        svcproxy.set_default_gateway(gwip)
    except Exception as e:
        err = "error restoring the default gateway: {0}".format( traceback.format_exc() )
        logging.error(err)


    return True

def handle_quit(sysTrayIcon):
    quitting = True
    # stop monitoring
    stop_monitor()
    logging.info('Bye, then.')
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



def main():
    global debug_level, trayapp

    import itertools, glob
    import shutil

    # read command line to determine debug level
    try:                                
        opts, args = getopt.getopt(sys.argv, "d", ["debug"])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-d', '--debug'):
            debug_level = logging.DEBUG

    # init logging capabilities
    #log_init_app(logging.DEBUG)

    #win32api.MessageBox(0, "CWD: %s\nOPENVPN_HOME: %s\sys.executable: %s" % (os.getcwd(),get_openvpn_home(), ) , 'Debug', 0x10)

    # make sure that TAP is installed
    if not windows_has_tap_device():
        logging.critical("TAP driver is not installed, please install.")
        win32api.MessageBox(window_handle(), _("I couldn't find the TAP/TUN driver for Windows.\n\nPlease install TAP for windows and try running this program again.\n\nhttp://openvpn.net/index.php/open-source/downloads.html"), _('TAP/TUN driver missing'), 0x10)
        sys.exit(1)

    start_monitor()

    #checkurl = config_check_url(config_file)
    #print("URL to check VPN connection %s ..." % (checkurl,))

    menu_options = ((_('Configure ...'), None, handle_configure, None),
                    
                    (_('Go online ...'), None, handle_go_online, None),
                    (_('Go offline ...'), None, handle_go_offline, win32con.MFS_DISABLED)
                   )
    
    trayapp = systray.SysTrayIcon(viper.ICONS['offline'], hover_text, menu_options, on_quit=handle_quit, default_menu_index=1)

    # # if we have an openVPN config file available, go online immediately
    # if config_exists():
    #     handle_go_online(trayapp)
    #     logging.debug("Config file found on startup, trying to auto-connect...")
    #     balloon.balloon_tip("Connecting...", "A default configuration was found, trying to connect automatically.")

    # !!! must call the loop function to enter the win32 message pump
    trayapp.loop()

def on_exit():
    """ exit handler takes care of restoring firewall state """
    logging.info("Restoring firewall state to permit traffic outside of the tunnel")
    try:
        svcproxy.firewall_down()
    except Exception as e:
        logging.error("Failed to restore firewall, we probably left the user out of internet: {0}".format(traceback.format_exc()))


if __name__ == '__main__':
    try:
        viper.ICONS = {
            'online' : get_resource_path('icons/online.ico'),
            'offline' : get_resource_path('icons/offline.ico'),
            'connecting' : get_resource_path('icons/connecting.ico'),
            'refresh' : get_resource_path('icons/refresh.ico')
        }

        atexit.register( on_exit )

        fn = os.path.join(get_user_cwd(), 'viperclient.log')
        logging.basicConfig(filename=fn, format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG, filemode="w+")

        # run the main loop if it's not already running otherwise tell the user
        if is_viper_running():
            win32api.MessageBox(window_handle(), _("Viper can only run once. I found another instance running, so I will stop now."), _('Viper can only run once'), 0x10)
            logging.warning("Another instance was running, will exit now.")
            sys.exit(3) # already running
        else:
            run_unique( main )
    except Exception as e:
        logging.critical( "Abnormal termination: {0}".format(traceback.format_exc()) )
    finally:
        # try to recover from bad crash and restore firewall if possible
        on_exit()
