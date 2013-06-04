#!/usr/bin/env python
import os
import logging
import servicemanager

DEFAULT_OPENVPN_HOME = "./openvpn/"

def log_init():
	logging.basicConfig(filename='ovpnmon.log',level=logging.DEBUG)

def get_openvpn_home():
	return os.getenv('OPENVPN_HOME', DEFAULT_OPENVPN_HOME)

def log(msg):
    #servicemanager.LogInfoMsg("SomeShortNameVersion - STOPPED!")
	servicemanager.LogInfoMsg(str(msg))
   