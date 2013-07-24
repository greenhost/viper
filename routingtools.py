#!/usr/bin/env python
"""Routing Table Tools for windows
"""

from os import popen
from re import match
from tools import log
from pprint import pprint

class InconsistentRoutingTable(Exception):
	pass

def get_default_route():
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
	return rtr_table[0]

def get_next_hop():
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
	return rtr_table[0][3]

def get_iface_route(ifaceip):
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if ifaceip in elem.strip()]
	return rtr_table

def filter_route(destination, netmask, iface):
	tab = get_iface_route(iface)
	retval = [row for row in tab if ( (row[0] == destination) and (row[1] == netmask))]
	return retval

# >>> routingtools.filter('0.0.0.0', '128.0.0.0', '172.26.37.6')
# [['0.0.0.0', '128.0.0.0', '172.26.37.5', '172.26.37.6', '30']]
# >>> routingtools.filter('128.0.0.0', '128.0.0.0', '172.26.37.6')
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
	# print(">"*65)
	# tab = get_iface_route(ifaceip)
	# print("Interface: %s" % ifaceip)
	# pprint(tab)
	# print(">"*65)

	route1 = filter_route("0.0.0.0", "128.0.0.0", ifaceip)
	route2 = filter_route("128.0.0.0", "128.0.0.0", ifaceip)

	if( (len(route1) == 1) and (len(route2) == 1) ):  # if one and only one route was found
		return True
	elif ( (len(route1) > 1) or (len(route2) > 1) ):
		raise InconsistentRoutingTable("A routing table with multiple entries for interface %s was found" % ifaceip)
	else:
		return False

