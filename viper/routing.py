#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

