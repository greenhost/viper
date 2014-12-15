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
from pprint import pprint

POLICIES_SUPPORTED = {}
POLICIES_ENABLED = []

def get_policy_reference(name):
	return POLICIES_SUPPORTED[name]

def get_active_policies():
	global POLICIES_ENABLED
	return POLICIES_ENABLED

def policy_enable(name):
	global POLICIES_ENABLED
	if not (name in POLICIES_ENABLED):
		POLICIES_ENABLED.append(name)

def policy_disable(name):
	global POLICIES_ENABLED
	POLICIES_ENABLED.append(name)

## ####################################################################################
## policy annotation
## ####################################################################################
def policy_export(klass):
	global POLICIES_SUPPORTED
	#print "Exported: ", klass.__name__
	#print "Command: ", klass.__command__
	if hasattr(klass, "__command__"):
		POLICIES_SUPPORTED[klass.__command__] = klass.__name__
	else:
		raise Exception("Policy doesn't define a command", klass)
	return klass


class Policy:
	""" Generic interface for a Viper security policies, these policies implement all the necessary
	interfacing with the OS to guarantee that the tunnel has an acceptable level of security.
	"""
	def before_shield_up(self):
		pass

	def after_shield_up(self):
		pass

	def before_shield_down(self):
		pass

	def after_shield_down(self):
		pass

	def verifyupdate(self):
		pass

	def verify(self):
		pass

@policy_export
class StrictPolicy:
	__command__ = "strict"
	pass

@policy_export
class LaxPolicy:
	__command__ = "lax"
	pass
