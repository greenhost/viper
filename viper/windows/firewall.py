#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
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
import os, sys
import win32com.client
import pythoncom
import logging
import subprocess

from viper import tools


# Return values of fwipv6 command:
# 0 = operation was successful
# 1 = operation failed
# 2 = firewall is not enabled

class FirewallException(Exception):
	pass

def is_firewall_enabled():
	"""Check whether windows firewall is enabled or not"""
	fw = win32com.client.gencache.EnsureDispatch('HNetCfg.FwMgr',0)
	fwprofile = fw.LocalPolicy.CurrentProfile
	return fwprofile.FirewallEnabled

def run_fwipv6(command):
	path = tools.get_viper_home()
	path = os.path.join(path, "utils/fwipv6")

	logging.debug("Executing fwipv6 at {0}...".format(path) )

	void = open(os.devnull, 'w')
	try:
		proc = subprocess.Popen([path, command], stdout=void, stderr=void)

		proc.wait()
		if (proc.returncode == 1) or (proc.returncode == 3):
			if proc.returncode == 1:
				msg = "Couldn't block IPv6 traffic (fwipv6 reports operation failed)"
			else:
				msg = "Couldn't block IPv6 traffic (fwipv6 reports firewall disabled)"

			# log error and propagate condition
			logging.error(msg)
			raise FirewallException(msg)
	except OSError, e:
		# @todo check if the exception above is actually raised by subprocess.Popen
		msg = "Couldn't execute subprocess '{}'".format(path)
		# log and propagate
		logging.critical(msg)
		raise FirewallException(msg)

def block_ipv6():
	"""Execute external fwipv6 tool to enable the Windows Firewall filtering of IPv6 traffic"""
	logging.info("Configuring Windows Firewall to block IPv6 traffic...")
	run_fwipv6("add")

def unblock_ipv6():
	"""Execute external fwipv6 tool to disable the Windows Firewall filtering of IPv6 traffic"""
	logging.info("Windows Firewall allows IPv6 traffic now...")
	run_fwipv6("remove")
