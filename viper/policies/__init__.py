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


## ###########################################################################
## events on enabled policies
## ###########################################################################
def before_open_tunnel():
    policies = get_active_policies()
    logging.debug("Running before_open_tunnel()")
    logging.debug("Contents of policies enabled: {0}".format(POLICIES_ENABLED) )
    for p in policies:
        logging.debug("Running before_open_tunnel on policy '{0}'".format(p) )
        try:
            p = get_policy_reference(p)
            p.before_open_tunnel()
        except Exception as ex:
            logging.exception("Failed to effect policies before_open_tunnel")
            return False

    return True

def after_open_tunnel():
    for p in get_active_policies():
        logging.debug("Running after_open_tunnel on policy '{0}'".format(p) )
        try:
            p = get_policy_reference(p)
            p.after_open_tunnel()
        except Exception as ex:
            logging.exception("Failed to effect policies after_open_tunnel")
            return False

    return True

def before_close_tunnel():
    for p in get_active_policies():
        logging.debug("Running before_close_tunnel on policy '{0}'".format(p) )
        try:
            p = get_policy_reference(p)
            p.before_close_tunnel()
        except Exception as ex:
            logging.exception("Failed to effect policies before_close_tunnel")
            return False

    return True

def after_close_tunnel():
    for p in get_active_policies():
        logging.debug("Running after_close_tunnel on policy '{0}'".format(p) )
        try:
            p = get_policy_reference(p)
            p.after_close_tunnel()
        except Exception as ex:
            logging.exception("Failed to effect policies after_close_tunnel")
            return False

    return True


def verifyloop():
    for p in get_active_policies():
        logging.debug("Running verifyloop on policy '{0}'".format(p) )
        try:
            p = get_policy_reference(p)
            p.verifyloop()
        except Exception as ex:
            logging.exception("Failed to effect policies verifyloop")
            return False

    return True

def verify():
    for p in get_active_policies():
        logging.debug("Running verify on policy '{0}'".format(p) )
        try:
            p = get_policy_reference(p)
            p.verify()
        except Exception as ex:
            logging.exception("Failed to effect policies verify")
            return False

    return True

## ###########################################################################
## policy annotation
## ###########################################################################
def policy_export(klass):
    global POLICIES_SUPPORTED
    #print "Exported: ", klass.__name__
    #print "Command: ", klass.__command__
    if hasattr(klass, "__command__"):
        POLICIES_SUPPORTED[klass.__command__] = klass() #klass.__name__
    else:
        raise Exception("Policy doesn't define a command", klass)
    return klass


## ###########################################################################
## interface
## ###########################################################################
class Policy:
    """ Generic interface for a Viper security policies, these policies implement all the necessary
    interfacing with the OS to guarantee that the tunnel has an acceptable level of security.
    """
    def before_open_tunnel(self):
        """
         This event gets called BEFORE the tunnel connection is opened
        :return: True if policy was enforced succesfully ""
        """
        pass

    def after_open_tunnel(self):
        """
         This event gets called AFTER the tunnel connection is opened
        :return: True if policy was enforced succesfully ""
        """
        pass

    def before_close_tunnel(self):
        """
         This event gets called BEFORE the tunnel connection is closed
        :return: True if policy was enforced succesfully ""
        """
        pass

    def after_close_tunnel(self):
        """
         This event gets called AFTER the tunnel connection is closed
        :return: True if policy was enforced succesfully ""
        """
        pass

    def verifyloop(self):
        """
         This event gets called on every run of the status loop
        :return: True if policy has been verified successfully ""
        """
        self.verify()

    def verify(self):
        """
         This gets called when we want to verify that the policy is in place
        :return: True if policy has been verified successfully ""
        """
        pass

