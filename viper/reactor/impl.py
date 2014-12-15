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
import os, sys, logging

from viper.windows import firewall
from viper import tools
from viper.openvpn import management, launcher


class Reactor:
    """ This service performs all the operations that have to run with elevated privileges, such as
    starting and stopping OpenVPN, interacting with firewall rules and routing tables, etc.
    """
    def __init__(self):
        logging.info("Initializing reactor...")
        self.launcher = launcher.OpenVPNLauncher()
        self.settings = {}

    def tunnel_open(self, cfgfile, logdir):
        """ Use launcher to start the OpenVPN instance 
        @param cfgfile location of OpenVPN configuration file in the file system
        @param logdir directory for log output
        """

        # flushing the dns cache doesn't harm and it can prevent dns leaks
        # @NOTE should we flush before connection is completed or should be flush only after new DNS
        # entries are injected by OpenVPN?
        tools.flush_dns()

        if not tools.is_openvpn_running():
            logging.debug("OpenVPN isn't running, trying to start process")
            
            tools.save_default_gateway()

            # configure the Windows Firewall to block all IPv6 traffic
            #firewall.block_ipv6()
            self.launcher.launch(cfgfile, logdir)
            # @TODOlaunch is async, perhaps this should be a callback
            #firewall.block_default_gateway()
        else:
            logging.debug("Another instance of OpenVPN was found, sending SIGHUP to force restart")
            handle = management.OVPNInterface()
            handle.hangup()
            del handle
            # if it's already running try to reaload it by sending hangup signal

    def tunnel_close(self):
        """ Use launcher to stop the OpenVPN process """
        self.launcher.terminate()

    def shields_up(self):
        """ Activate the firewall rules that will enhance the user's protection through the duration of the VPN run """
        logging.debug("Putting up firewall")

        # if Windows Firewall is not enabled, refuse to connect
        if not firewall.is_firewall_enabled():
            logging.critical("Firewall is not enabled. I will not connect.")
            return False
        else:
            # configure the Windows Firewall to block all IPv6 traffic
            firewall.block_ipv6()
            # @TODO launch is async, perhaps this should be a callback
            firewall.block_default_gateway("none-specified")

    def shields_down(self):
        """ Deactivate the firewall rules """
        logging.debug("Taking down firewall")
        # allow IPv6 traffic again
        firewall.unblock_ipv6()
        firewall.unblock_default_gateway("none-specified")