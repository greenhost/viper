#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""
Routing Table Tools for Windows. These are used to cross-check that
Internet traffic is correctly routed.

This is how a normal IPv4 routing table looks like

Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0    192.168.2.254      192.168.2.1     25
        127.0.0.0        255.0.0.0         On-link         127.0.0.1    306
        127.0.0.1  255.255.255.255         On-link         127.0.0.1    306
        [...]		[...]					[...]			[...]		[...]
  255.255.255.255  255.255.255.255         On-link       192.168.2.1    281

The routes marked as 'On-link' do not need a gateway because they are local. Windows
lists the routes in an inverse order to Linux based systems. Linux links the 
default route last and lists them in the order of prevalence, on Windows they are 
listed in reverse to their order of prevalence.

When OpenVPN is running in EIP mode and all internet traffic is channeled through it
a routing trick is added to the table. In addition to your default route:

          0.0.0.0          0.0.0.0    192.168.2.254      192.168.2.1     25

You will see at least two new ones with the same gateway and the same interface:

          0.0.0.0        128.0.0.0     172.xx.xx.xx     172.yy.yy.yy     30
        128.0.0.0        128.0.0.0     172.xx.xx.xx     172.yy.yy.yy     30

These routes are pushed by the OpenVPN server and basically override your
default route forcing all Internet traffic to go from your 
interface (172.yy.yy.yy) through the VPN gateway (172.xx.xx.xx).

If these routes do not exist in your routing table while you are connected to 
the VPN, you might be leaking traffic through your default route unknowingly.
"""
import logging
from os import popen
from re import match
from pprint import pprint

class InconsistentRoutingTable(Exception):
	pass

def get_default_route():
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
	# on windows the default route is always listed first
	return rtr_table[0]

def get_all_routes():
	retval = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
	return retval

def get_iface_route(ifaceip):
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if ifaceip in elem.strip()]
	return rtr_table

def get_default_route():
	routes = get_all_routes()
	for route in routes:
		if (route[0] == '0.0.0.0') and (route[1] == '0.0.0.0'): 
			return route

	return None

def filter_route(destination, netmask, iface):
	tab = get_iface_route(iface)
	retval = [row for row in tab if ( (row[0] == destination) and (row[1] == netmask))]
	return retval

def verify_vpn_routing_table(ifaceip):
	""" 
	Given an interface address that we obtain from querying OpenVPN, we should check for the existence of
	two (and only two) entries in the routing table.
	destination			netmask			iface
	0.0.0.0             128.0.0.0       <given>
	128.0.0.0           128.0.0.0       <given>

	If we find more than one of these then our routing table is corrupted, this might be from a OpenVPN 
	run that didn't close properly.
	"""
	route1 = filter_route("0.0.0.0", "128.0.0.0", ifaceip)
	route2 = filter_route("128.0.0.0", "128.0.0.0", ifaceip)

	if( (len(route1) == 1) and (len(route2) == 1) ):  # if one and only one route was found
		logging.debug("Verifying routing table for interface '%s': PASSED" % ifaceip)
		return True
	# the following condition might not be true, some providers might provide
	# several of these routes for redundancy's sake. Viper wants to be
	# conservative about this and wants to make sure that only one EIP gateway exists.
	elif ( (len(route1) > 1) or (len(route2) > 1) ):
		raise InconsistentRoutingTable("A routing table with multiple entries for interface %s was found" % ifaceip)
	else:
		logging.debug("Verifying routing table for interface '%s': FAILED" % ifaceip)
		return False

