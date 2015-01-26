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
import os, sys
from os import popen
import logging
import platform

import viper

try:
    import appdirs
except ImportError:
    print("appdirs module is required. Please see: https://pypi.python.org/pypi/appdirs/")

if platform.system() == "Windows":
    try:
        import servicemanager
    except ImportError:
        print("Couldn't import servicemanager, you are probably not on windows")

try:
    import psutil
except ImportError:
    print("psutil module is required for process tracking. Please see: https://code.google.com/p/psutil/")


# useful globals
PRODUCT_NAME = "Viper"
PRODUCER_NAME = "Greenhost"
DEFAULT_OPENVPN_HOME = "./openvpn/"
DEFAULT_VIPER_HOME = "./"

WINREG_KEY_NAME = r'Software\Viper'

def save_last_config(tunname, tunconfig, tunpolicy):
    """ Save last known configuration in Windows registry, if the key isn't found it will be created """
    if viper.IS_WIN:
        import _winreg as winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, WINREG_KEY_NAME, 0, winreg.KEY_ALL_ACCESS)
        except:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, WINREG_KEY_NAME)
        finally:
            winreg.SetValueEx(key, "TunnelName", 0, winreg.REG_SZ, tunname)
            winreg.SetValueEx(key, "TunnelConfig", 0, winreg.REG_SZ, tunconfig)
            winreg.SetValueEx(key, "TunnelSecPolicy", 0, winreg.REG_SZ, tunpolicy)
            winreg.CloseKey(key)

def load_last_config():
    """ Load last known configuration from the registry, throws a WindowsError exception if key wasn't found in registry """
    retval = None
    if viper.IS_WIN:
        import _winreg as winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, WINREG_KEY_NAME, 0, winreg.KEY_ALL_ACCESS)
            # QueryValueEx returns a tuple containing 0: value, 1: type (e.g. REG_SZ)
            tunname   = winreg.QueryValueEx(key, "TunnelName")[0]
            tunconfig = winreg.QueryValueEx(key, "TunnelConfig")[0]
            tunpolicy = winreg.QueryValueEx(key, "TunnelSecPolicy")[0]
            retval = (tunname, tunconfig, tunpolicy)
        except ImportError, e:
            logging.error("Failed to import _winreg library. Cannot load last active policy")
    else:
        logging.error("policy_load_last is not supported in this OS")

    return retval


def is_viper_running():
    """Make sure that no other instance of Viper is being executed at the moment"""
    lockfile = os.path.join(get_user_cwd(), 'pidlock')
    logging.debug("Check if we are already running...")
    if os.path.isfile( lockfile ):
        # open file and read PID from it
        with open(lockfile, 'r') as f:
            content = f.read()
            pid = int(content)
            try:
                # if process is found with the PID, there's another instance running
                proc = psutil.Process(pid)
                return True
            except psutil.NoSuchProcess as e:
                # pidfile is tale, delete it
                # we can now assume there's not another version of viper running
                f.close()
                os.unlink(lockfile)
                return False
    else:
        return False

def run_unique(fn):
    """ Run a python method by making sure it's only run once """
    lockfile = os.path.join(get_user_cwd(), 'pidlock')
    try:
        with file(lockfile, 'w') as flock:
            flock.write( str(os.getpid()) )
        # execute main loop
        fn()
    finally:
        os.unlink(lockfile)

def is_openvpn_running():
    """Check that the OpenVPN process is only run once"""
    try:
        procs = []
        for p in list(psutil.process_iter()): #psutil.get_process_list():
            try:
                if p.name() and ('openvpn' in p.name().lower()):
                    procs.append(p)
            except psutil.AccessDenied as e:
                # we have no rights to peer into this process, skip to next
                continue
        return procs
    except psutil.NoSuchProcess as e:
        return False

def log_init_app(lvl=logging.DEBUG):
    fn = os.path.join(get_user_cwd(), 'viperclient.log')
    print("Trying to log to file %s, with level %s" % (fn, lvl))
    logging.basicConfig(filename=fn, format='%(asctime)s %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=lvl, filemode="w+")

def log_init_service(level=logging.DEBUG, logfile="c:\ovpnmon.log"):
    #fmt = "%(asctime)-15s - %(levelname)s - %(user)-8s - %(message)s"
    logging.basicConfig(filename=logfile, level=level, filemode="w+")

def get_viper_home():
    """Get location of the Viper install root"""
    return os.getenv('VIPER_HOME', DEFAULT_VIPER_HOME)

def get_openvpn_home():
    """ Get location of OpenVPN executable """
    return os.getenv('OPENVPN_HOME', DEFAULT_OPENVPN_HOME)

def get_my_cwd():
    """ Get the working directory of the current executable """
    return os.path.dirname(sys.executable)

def get_user_cwd():
    """ Get user working directory """
    d = appdirs.AppDirs(PRODUCT_NAME, "") #, PRODUCER_NAME)

    if not os.path.exists(d.user_data_dir):
        os.makedirs(d.user_data_dir)

    return d.user_data_dir

def get_resource_path(res):
    """Get path to program resources on disk
    On windows this is a little tricky because
    windows processes are executes from 
    C:\windows\system32 apparently, so we have to get our resources
    from the install path.
    """
    rpath = os.path.join(get_my_cwd(), "resources")
    return os.path.join(rpath, res)

def flush_dns():
    """ Instruct Windows to flush the DNS cache
    :return True: is flushing is Successfully
    :return False: otherwise 
    """
    logging.debug("Flushing DNS cache...")
    res = popen("ipconfig /flushdns").read().split()
    return True if 'Successfully' in res else False  # tested on windows 8 and windows 7

def log(msg):
    """Send message to the Windows Event Log"""
    servicemanager.LogInfoMsg(str(msg))


def windows_has_tap_device():
    """
    Loops over the windows registry trying to find if the tap0901 tap driver
    has been installed on this machine.
    """
    import _winreg as reg

    adapter_key = 'SYSTEM\CurrentControlSet\Control\Class' \
        '\{4D36E972-E325-11CE-BFC1-08002BE10318}'
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, adapter_key) as adapters:
        try:
            for i in xrange(10000):
                key_name = reg.EnumKey(adapters, i)
                with reg.OpenKey(adapters, key_name) as adapter:
                    try:
                        component_id = reg.QueryValueEx(adapter,
                                                        'ComponentId')[0]
                        if component_id.startswith("tap0901"):
                            return True
                    except WindowsError:
                        pass
        except WindowsError:
            pass
    return False

def sanitize_ip(ipaddr):
    """
    Make sure the IP address is a dot-separated numeric quad
    """
    quad = [int(byte) for byte in ipaddr.split(".")]
    return "%d.%d.%d.%d" % tuple(quad)


## ##########################################################################
## Routing stack helpers
## ##########################################################################
def save_default_gateway():
    from viper import routing
    defaultgw = os.path.join(get_user_cwd(), 'defaultgw')
    gwip = routing.get_default_gateway()
    try:
        with file(defaultgw, 'w+') as f:
            f.write( str(gwip) )
    except Exception as e:
        logging.info("Failed to save default gateway to file {0}".format(defaultgw))

def recover_default_gateway():
    """ 
    Get the last known default gateway configuration from a file on disk

    :returns: IP address of the default gateway if found, None if nothing is found
    """
    defaultgw = os.path.join(get_user_cwd(), 'defaultgw')
    try:
        if os.path.isfile( defaultgw ):
            with open(defaultgw, 'r') as f:
                content = f.read()
                return sanitize_ip( str(content) )
        else:
            return None
    except Exception as e:
        logging.info("Failed to load default gateway from file {0}".format(defaultgw))
        return None
    finally:
        os.unlink(defaultgw)

def delete_default_gateway():
    from viper import routing
    save_default_gateway()
    gwip = routing.get_default_gateway()
    route_del("0.0.0.0", "0.0.0.0", gwip)

def restore_default_gateway():
    gwip = recover_default_gateway()
    route_add("0.0.0.0", "0.0.0.0", gwip)

