#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from viper import routing
from viper.openvpn import monitor
from viper.tools import *
import traceback

SERVICE = None

def start():
	global SERVICE
	from rpyc.utils.server import ThreadedServer
	logging.info("OVPN START...")
	# make sure only connections from localhost are accepted
	SERVICE = ThreadedServer(monitor.RPCService, hostname = 'localhost', port = 18861)

def stop():
	global SERVICE
	logging.info("OVPN STOP...")
	SERVICE.close()

if __name__ == '__main__':
	#log_init_service()
	logging.basicConfig(level=logging.DEBUG)
	start()
	while 1:
		time.sleep(200)
