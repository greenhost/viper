#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @license
#
import os, sys
import logging
import servicemanager
import appdirs

try:
    import psutil
except ImportError:
    print("psutil module is required for process tracking. Please see: https://code.google.com/p/psutil/")


# useful globals
PRODUCT_NAME = "Viper"
PRODUCER_NAME = "Greenhost"
DEFAULT_OPENVPN_HOME = "./openvpn/"
DEFAULT_VIPER_HOME = "./"

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
            except psutil.NoSuchProcess, e:
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
    procs = [p for p in psutil.get_process_list() if 'openvpn' in p.name]
    return procs

def log_init_app(level=logging.DEBUG):
    fn = os.path.join(get_user_cwd(), 'umanviper.log')
    logging.basicConfig(filename=fn, level=level)

def log_init_service(level=logging.DEBUG):
    #fmt = "%(asctime)-15s - %(levelname)s - %(user)-8s - %(message)s"
    logging.basicConfig(filename='c:\ovpnmon.log', level=level)

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
    d = appdirs.AppDirs(PRODUCT_NAME, PRODUCER_NAME)

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

