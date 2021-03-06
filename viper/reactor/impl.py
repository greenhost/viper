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
from viper import policies

class Reactor:
    """ This service performs all the operations that have to run with elevated privileges, such as
    starting and stopping OpenVPN, interacting with firewall rules and routing tables, etc.
    """
    def __init__(self):
        logging.info("Initializing reactor...")

        # Reactor keeps track of these state variables
        self.last_known_gateway = None
        self.ovpn_state = None

        try:
            from viper.openvpn import launcher, management
            self.launcher = launcher.OpenVPNLauncher()
            self.poll = management.OVPNInterface(self.set_last_known_gateway, self.set_ovpn_status)
        except ImportError as e:
            logging.critical("Couldn't import OpenVPN launcher")

        self.settings = {}
        try:
            if not firewall.is_firewall_enabled():
                 logging.critical("Firewall is not enabled. I will not connect.")
        except firewall.FirewallException as ex:
            logging.exception("Failed to check firewall")

        # see if we have a previous configuration we can use
        cfg = tools.load_last_config()
        # if so start the tunnel right away with it
        if cfg:
            logging.debug("Found a default config from a previous run, opening tunnel with this config...")
            self.tunnel_open(cfg[1], cfg[2])
        else:
            logging.debug("Previous configuration was not found, waiting for further instructions")


    def set_last_known_gateway(self, gwip):
        self.last_known_gateway = gwip

    def set_ovpn_status(self, state):
        self.ovpn_state = state

    def get_tunnel_status(self):
        st = {'tunnel': 'DISCONNECTED', 'openvpn': 'DISCONNECTED'}
        ovpnst = self.poll.poll_status(self.last_known_gateway)
        
        if 'ovpn_state' in ovpnst:
            st['tunnel']  = ovpnst['ovpn_state']
            st['openvpn'] = ovpnst['ovpn_state']

        return st

    def tunnel_open(self, cfgfile, logdir):
        """ Use launcher to start the OpenVPN instance 
        @param cfgfile location of OpenVPN configuration file in the file system
        @param logdir directory for log output
        """
        from viper.openvpn import launcher
        # flushing the dns cache doesn't harm and it can prevent dns leaks
        # @NOTE should we flush before connection is completed or should be flush only after new DNS
        # entries are injected by OpenVPN?
        tools.flush_dns()

        if not tools.is_openvpn_running():
            logging.debug("OpenVPN isn't running, trying to start process")
            
            tools.save_default_gateway()
            logging.debug("Saving default gateway.")
            # enforce active policies before the tunnel goes up
            if policies.before_open_tunnel():
                # open tunnel
                logging.debug("Open tunnel...")
                try:
                    self.launcher.launch(cfgfile, logdir)
                except launcher.OpenVPNNotFoundException as ex:
                    ovpnhome = tools.get_openvpn_home()
                    logging.critical("Couldn't find openvpn excutable [OVPN_HOME={0}]".format(ovpnhome) )

                if not policies.after_open_tunnel():
                    logging.warning("Failed to enforce policies AFTER opening tunnel")

                # if we got this far, save this config as default for next run
                tools.save_last_config("default", cfgfile, logdir)
            else:
                logging.debug("Failed to enforce policies BEFORE opening tunnel")
        else:
            logging.debug("Another instance of OpenVPN was found, sending SIGHUP to force restart")
            # @NOTE this import is here to prevent circular module inclusion
            try:
                from viper.openvpn import management
                handle = management.OVPNInterface()
                handle.hangup()
                del handle
                # if it's already running try to reaload it by sending hangup signal
            except ImportError, e:
                logging.critical("Couldn't import management interface module")

    def tunnel_close(self):
        """ Use launcher to stop the OpenVPN process """
        if not policies.before_close_tunnel():
            logging.warning("Failed to enforce policies BEFORE closing tunnel connection")
        self.launcher.terminate()
        if not policies.after_close_tunnel():
            logging.warning("Failed to enforce policies AFTER closing tunnel connection")

