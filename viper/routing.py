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
"""
import logging
from os import popen
from re import match
from pprint import pprint
import subprocess

class InconsistentRoutingTable(Exception):
	pass

# def get_default_route():
# 	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
# 	# on windows the default route is always listed first
# 	return rtr_table[0]

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

def get_default_gateway():
	"""
	Obtain the ip address of the current default gateway
	"""
	rt = get_default_route()
	return rt[2] if len(rt) > 2 else None

def filter_route(destination, netmask, iface):
	tab = get_iface_route(iface)
	retval = [row for row in tab if ( (row[0] == destination) and (row[1] == netmask))]
	return retval


def delete_default_gateway(self):
    save_default_gateway()
    route_del("0.0.0.0", "0.0.0.0")

def restore_default_gateway(self):
    route_add("0.0.0.0", "0.0.0.0")


def route_add(self, net, mask="255.255.255.255", dest):
    dst = sanitise_addr(dest)
    cmd = "route add %s mask %s %s" % (net, mask, dst)
    subprocess.call(cmd, shell=True)

def route_del(self, net, mask="255.255.255.255", dest):
    dst = sanitise_addr(dest)
    cmd = "route delete %s mask %s %s" % (net, mask, dst)
    subprocess.call(cmd.split(), shell=True)

## ######################################################################################
## Filter implementations
## ######################################################################################
class VerifyTwoRoutes:
	""" 
	This is a pass filter. Given an interface address that we obtain from querying OpenVPN, we should check for the existence of
	two (and only two) entries in the routing table.
	destination			netmask			iface
	0.0.0.0             128.0.0.0       <given>
	128.0.0.0           128.0.0.0       <given>

	If we find more than one of these then our routing table is corrupted, this might be from a OpenVPN 
	run that didn't close properly.
	"""
	def __init__(self, ifaceip):
		self.interface = ifaceip

	def pass(self):
		route1 = filter_route("0.0.0.0", "128.0.0.0", self.interface)
		route2 = filter_route("128.0.0.0", "128.0.0.0", self.interface)

		if( (len(route1) == 1) and (len(route2) == 1) ):  # if one and only one route was found
			logging.debug("Verifying routing table for interface '%s': PASSED" % self.interface)
			return True
		# the following condition might not be true, some providers might provide
		# several of these routes for redundancy's sake. Viper wants to be
		# conservative about this and wants to make sure that only one EIP gateway exists.
		elif ( (len(route1) > 1) or (len(route2) > 1) ):
			raise InconsistentRoutingTable("A routing table with multiple entries for interface %s was found" % self.interface)
		else:
			logging.debug("Verifying routing table for interface '%s': FAILED" % self.interface)
			return False

class VerifyDefaultGateway:
	"""
	Makes sure there is a single default gateway entry in the routing table
	"""
	def __init__(gwip):
		self.gateway_ip = gwip

	def pass(self):
		defroute = filter_route("0.0.0.0", "0.0.0.0", self.gateway_ip)
		if( len(defroute) == 1 ):
			logging.debug("Verifying default gateway '%s': PASSED" % self.gateway_ip)
			return True
		else:
			logging.debug("Verifying default gateway '%s': FAILED" % self.gateway_ip)
			return False

