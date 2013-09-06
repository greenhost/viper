#!/usr/bin/env python
import os, sys, re

"""This script is meant to be run from the command line on windows, not as an executable"""
import logging
from pprint import pprint
import viper
from viper import tools
from viperclient import *

if __name__ == '__main__':
	viper.ICONS = {
	    'online' : 'online.ico',
	    'offline' : 'offline.ico',
	    'connecting' : 'connecting.ico',
	    'refresh' : 'refresh.ico'
	}
	print(sys.argv[0])
	pprint(viper.ICONS)
	# init logging capabilities
	logging.basicConfig(level=logging.DEBUG)

	if tools.is_viper_running():
		sys.exit(3) # already running
	else:
		tools.run_unique( main )
