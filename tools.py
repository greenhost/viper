#!/usr/bin/env python
import os

DEFAULT_OPENVPN_HOME = "./openvpn/"

def get_openvpn_home():
	return os.getenv('OPENVPN_HOME', DEFAULT_OPENVPN_HOME)

def log(msg):
    #servicemanager.LogInfoMsg("SomeShortNameVersion - STOPPED!")
    print(msg)
   