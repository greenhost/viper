#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
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
import os, sys
import logging
import subprocess

from viper import tools


# Return values of fwipv6 command:
# 0 = operation was successful
# 1 = operation failed
# 2 = firewall is not enabled

class FirewallException(Exception):
    pass

def is_firewall_enabled():
    """Check whether windows firewall is enabled or not"""
    try:
        cmd = subprocess.Popen(['netsh', 'advfirewall', 'show', 'currentprofile'], stdout=subprocess.PIPE)
        out = cmd.stdout.readlines()

        for l in out:
            if l.startswith('State'):
                state = l.split()[-1]

        if state == "ON":
            return True
        else:
            return False
    except OSError as ex:
        raise FirewallException("Couldn't determine if firewall is up")

def set_firewall_state(state = "on"):
    """ Elevated privileges needed to run this 
    @note uses the netsh command to interact with the firewall which is notorious for changing acrsso versions of windows
    """
    cmd = "netsh advfirewall set allprofiles state {0}".format(state)
    subprocess.call( cmd.split() )

def firewall_enable():
    set_firewall_state("on")

def firewall_disable():
    set_firewall_state("off")

def block_ipv6():
    """Execute external fwipv6 tool to enable the Windows Firewall filtering of IPv6 traffic"""
    rules = [
        "netsh advfirewall firewall add rule name=\"Viper - IPv6\" protocol=icmpv6 dir=out action=block",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6\" protocol=icmpv6 dir=in action=block",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6\" action=block protocol=41 dir=out",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6 protocol 43\" protocol=43 action=block dir=out",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6 protocol 44\" protocol=44 action=block dir=out",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6 protocol 58\" protocol=58 action=block dir=out",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6 protocol 59\" protocol=59 action=block dir=out",
        "netsh advfirewall firewall add rule name=\"Viper - IPv6 protocol 60\" protocol=60 action=block dir=out"
    ]

    logging.info("Configuring Windows Firewall to block IPv6 traffic...")
    for r in rules:
        retval = subprocess.call( r.split() )
        if retval != 0:
            # if setting one of the rules fails, return
            return False

    return True

def exec_rules(rules):
    for r in rules:
        retval = subprocess.call( r.split() )
        if retval != 0:
            # if setting one of the rules fails, return
            return False

    return True

def unblock_ipv6():
    """Execute external fwipv6 tool to disable the Windows Firewall filtering of IPv6 traffic"""
    rules = [
        "netsh advfirewall firewall delete rule name=\"Viper - IPv6\"",
        "netsh advfirewall firewall delete rule name=\"Viper - IPv6 protocol 43\"",
        "netsh advfirewall firewall delete rule name=\"Viper - IPv6 protocol 44\"",
        "netsh advfirewall firewall delete rule name=\"Viper - IPv6 protocol 58\"",
        "netsh advfirewall firewall delete rule name=\"Viper - IPv6 protocol 59\"",
        "netsh advfirewall firewall delete rule name=\"Viper - IPv6 protocol 60\""
    ]

    logging.info("Windows Firewall allows IPv6 traffic now...")
    return exec_rules( rules )

def block_default_local_subnet(interface_ip):
    rules = [
        "netsh advfirewall firewall add rule name=\"Viper - Block local subnet\" action=block protocol=any dir=out localip=any remoteip=LocalSubnet",
    ]
    logging.info("Blocking all traffic on the local subnet (gateway ip: {0})".format(interface_ip))
    return exec_rules( rules )

def unblock_default_local_subnet(interface_ip):
    rules = [
        "netsh advfirewall firewall delete rule name=\"Viper - Block local subnet\"",
    ]
    logging.info("Unblocking local subnet (gateway ip: {0})".format(interface_ip))
    return exec_rules( rules )

def block_all_ports_except_vpn(vpn_port):
    logging.info("Blocking all ports except the VPN's (vpn port: {0})".format(vpn_port))
    pass

def unblock_all_ports():
    logging.info("Unblocking all ports")
    pass
