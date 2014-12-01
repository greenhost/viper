#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from pprint import pprint

POLICIES_SUPPORTED = {}
POLICIES_ENABLED = []

def get_active_policies():
	global POLICIES_ENABLED
	return POLICIES_ENABLED

def policy_enable(name):
	global POLICIES_ENABLED
	if not (name in POLICIES_ENABLED):
		POLICIES_ENABLED.append(name)

def policy_disabled(name):
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
	def before_shield_up():
		pass

	def after_shield_up():
		pass

	def before_shield_down():
		pass

	def after_shield_down():
		pass

	def checkupdate():
		pass

	def check():
		pass

@policy_export
class StrictPolicy:
	__command__ = "strict"
	pass

@policy_export
class LaxPolicy:
	__command__ = "lax"
	pass

@policy_export
class IPv6Policy(Policy):
	__command__ = "ipv6-off"
	def before_shield_up():
		check()

	def after_shield_up():
		pass

	def before_shield_down():
		pass

	def after_shield_down():
		pass

	def checkupdate():
		pass

	def check():
	    logging.info("Checking fw entries for IPv6")

@policy_export
class GatewayPolicy(Policy):
	__command__ = "gateway-monitor"
	def before_shield_up():
		check()

	def after_shield_up():
		pass

	def before_shield_down():
		pass

	def after_shield_down():
		pass

	def checkupdate():
		check()

	def check():
	    logging.info("Checking that gateway hasn't changed")

@policy_export
class CrossCheckPolicy(Policy):
	__command__ = "cross-check"
	def before_shield_up():
		check()

	def after_shield_up():
		pass

	def before_shield_down():
		pass

	def after_shield_down():
		pass

	def checkupdate():
		check()

	def check():
	    logging.info("Cross checking that def. gateway matches OpenVPNs expectations")


# @policy_export
# class UnknownPolicy(Policy):
# 	pass


if __name__ == '__main__':
	print "::: POLICIES :::"

	for k, v in POLICIES_SUPPORTED.iteritems():
		print "policy name [", k, "] // policy class [", v, "]"
	pass
