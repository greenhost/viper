#!/usr/bin/env python
# -*- coding: utf-8 -*-
from viper import routing
from viper.windows import service
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
	logging.info("OVPN STOP...")
	SERVICE.close()

if __name__ == '__main__':
	#log_init_service()
	logging.basicConfig(level=logging.DEBUG)
	start()
