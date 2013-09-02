#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

def is_viper_running():
    lockfile = os.path.join(get_user_cwd(), 'pidlock')
    logging.debug("Check if we are already running '%s'" % (lockfile,))
    return os.path.isfile( lockfile )

def run_unique(fn):
    lockfile = os.path.join(get_user_cwd(), 'pidlock')
    try:
        with file(lockfile, 'w') as flock:
            flock.write( str(os.getpid()) )
        # execute main loop
        fn()
    finally:
        os.unlink(lockfile)

def is_openvpn_running():
    procs = [p for p in psutil.get_process_list() if 'openvpn' in p.name]
    return procs

def log_init_app(level=logging.DEBUG):
    fn = os.path.join(get_user_cwd(), 'umanviper.log')
    logging.basicConfig(filename=fn, level=level)

def log_init_service(level=logging.DEBUG):
    #fmt = "%(asctime)-15s - %(levelname)s - %(user)-8s - %(message)s"
    logging.basicConfig(filename='c:\ovpnmon.log', level=level)

def get_openvpn_home():
	return os.getenv('OPENVPN_HOME', DEFAULT_OPENVPN_HOME)

def get_my_cwd():
	return os.path.dirname(sys.executable)

def get_user_cwd():
	d = appdirs.AppDirs(PRODUCT_NAME, PRODUCER_NAME)
	
	if not os.path.exists(d.user_data_dir):
		os.makedirs(d.user_data_dir)

	return d.user_data_dir

def log(msg):
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

