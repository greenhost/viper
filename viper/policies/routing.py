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
import logging
from os import popen
from re import match
from pprint import pprint
from viper.tools import *
import subprocess

import viper.routing import *

@policy_export
class GatewayPolicy(Policy):
	__command__ = "gateway-monitor"
	def before_shield_up(self):
		self.verify(self)

	def after_shield_up(self):
		pass

	def before_shield_down(self):
		pass

	def after_shield_down(self):
		pass

	def verifyupdate(self):
		self.verify()

	def verify(self):
	    logging.info("Checking that gateway hasn't changed")

@policy_export
class CrossCheckPolicy(Policy):
	__command__ = "cross-check"
	def before_shield_up(self):
		self.verify()

	def after_shield_up(self):
		pass

	def before_shield_down(self):
		pass

	def after_shield_down(self):
		pass

	def verifyupdate(self):
		self.verify()

	def verify(self):
	    logging.info("Cross checking that def. gateway matches OpenVPNs expectations")


@policy_export
class MonitorSplitRoutes:
	__command__ = "split-route"
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

	def verify(self):
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

@policy_export
class MonitorDefaultGateway:
	__command__ = "unmutable-gateway"
	"""
	Makes sure there is a single default gateway entry in the routing table
	"""
	def __init__(self, gwip):
		self.gateway_ip = gwip

	def verify(self):
		defroute = filter_route("0.0.0.0", "0.0.0.0", self.gateway_ip)
		if( len(defroute) == 1 ):
			logging.debug("Verifying default gateway '%s': PASSED" % self.gateway_ip)
			return True
		else:
			logging.debug("Verifying default gateway '%s': FAILED" % self.gateway_ip)
			return False

