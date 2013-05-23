#!/usr/bin/env python
"""Routing Table Tools for windows
"""

from os import popen
from re import match


def get_default_route():
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
	return rtr_table[0]

def get_next_hop():
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if match("^[0-9]", elem.strip())]
	return rtr_table[0][3]

def get_iface_route(ifaceip):
	rtr_table = [elem.strip().split() for elem in popen("route print").read().split("Metric\n")[1].split("\n") if ifaceip in elem.strip()]
	return rtr_table

def verify_iface_vpn_routing_table(ifaceip):
	tab = get_iface_route(ifaceip)