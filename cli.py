#!/usr/bin/env python
import os, sys, re

"""This script is meant to be run from the command line on windows, not as an executable"""
import logging
from pprint import pprint
import viper
from viper import tools
from viperclient import *

def cwd():
	return os.path.dirname(os.path.realpath(__file__))

def icon_path():
	return os.path.join(cwd(), "resources/icons")

if __name__ == '__main__':
	viper.ICONS = {
	    'online' : os.path.join(icon_path(), 'online.ico'),
	    'offline' : os.path.join(icon_path(), 'offline.ico'),
	    'connecting' : os.path.join(icon_path(), 'connecting.ico'),
	    'refresh' : os.path.join(icon_path(), 'refresh.ico')
	}

	print(sys.argv[0])
	pprint(viper.ICONS)
	# init logging capabilities
	logging.basicConfig(level=logging.DEBUG)

	if tools.is_viper_running():
		sys.exit(3) # already running
	else:
		tools.run_unique( main )
