#!/usr/bin/env python
import os, sys
import logging
import servicemanager
import appdirs

# useful globals
PRODUCT_NAME = "UmanViper"
PRODUCER_NAME = "Greenhost"
DEFAULT_OPENVPN_HOME = "./openvpn/"

def log_init():
	logging.basicConfig(filename='ovpnmon.log',level=logging.DEBUG)

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
    #servicemanager.LogInfoMsg("SomeShortNameVersion - STOPPED!")
	servicemanager.LogInfoMsg(str(msg))
   