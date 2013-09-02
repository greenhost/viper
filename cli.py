#!/usr/bin/env python
import os, sys, re

"""This script is meant to be run from the command line on windows, not as an executable"""
import logging
from viper.tools import *
from umanager import *

ICONS = {
    'online' : 'online.ico',
    'offline' : 'offline.ico',
    'connecting' : 'connecting.ico',
    'refresh' : 'refresh.ico'
}

if __name__ == '__main__':
	print(sys.argv[0])
	# init logging capabilities
	logging.basicConfig(level=logging.DEBUG)

	if is_viper_running():
		sys.exit(3) # already running
	else:
		run_unique( main )
