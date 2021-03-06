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
from viper.tools import *
import subprocess

class InconsistentRoutingTable(Exception):
	pass

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

def route_add(net, mask, dest):
    dst = sanitize_ip(dest)
    cmd = "route add %s mask %s %s" % (net, mask, dst)
    logging.debug("Adding route (net {0}, mask {1}, dst {2})".format(net, mask, dst))
    subprocess.call(cmd, shell=True)

def route_del(net, mask, dest):
    dst = sanitize_ip(dest)
    cmd = "route delete %s mask %s %s" % (net, mask, dst)
    logging.debug("Removing route (net {0}, mask {1}, dst {2})".format(net, mask, dst))
    subprocess.call(cmd.split(), shell=True)

def set_default_gateway(self, gwip):
	"""
	 Add a default gateway to the routing table of the current interface
	:param gwip: ip address of the default gateway
	"""
	logging.debug("Setting default gateway to '{0}'".format(gwip))
	route_add("0.0.0.0", "0.0.0.0", gwip)
