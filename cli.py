#!/usr/bin/env python
#
# Copyright (c) 2013 Greenhost VOF and contributors
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.
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
	logging.basicConfig(level=logging.DEBUG)

	if tools.is_viper_running():
		sys.exit(3) # already running
	else:
		tools.run_unique( main )
