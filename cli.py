#!/usr/bin/env python
#
# Copyright (c) 2013 Greenhost VOF
# https://greenhost.nl -\- https://greenhost.io
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', level=logging.DEBUG)

	if tools.is_viper_running():
		sys.exit(3) # already running
	else:
		tools.run_unique( main )
