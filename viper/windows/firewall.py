#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
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
