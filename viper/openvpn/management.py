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
Polls status of OpenVPN using the management socket interface.
"""
import string
import socket
import time

from viper.tools import *
#from viper import reactor

class OVPNInterface:
    def __init__(self, cb_last_gateway = None, cb_set_ovpn_status = None):
        self.connected = False
        self.sock = None
        self.retries = 0
        self.gateway_monitor = None
        self.cb_last_gateway = cb_last_gateway
        self.cb_set_ovpn_status = cb_set_ovpn_status

    def send(self, command, connection_timeout = .5, response_delay = .5):
        retval = None
        try:
            self.sock = socket.socket()
            logging.debug("Trying to connect to OVPN management socket")
            if self.sock: self.sock.settimeout( connection_timeout )
            if self.sock: self.sock.connect(("localhost", 7505))
            # sock.setblocking(1)
            self.connected = True

            logging.debug("Connected successfully to management socket")

            count = 0
            if self.sock: count = self.sock.send(command)
            if count == 0:
                logging.debug("Couldn't send message through socket")
            time.sleep( response_delay ) # must wait a bit otherwise we will not get a response to our request

            if self.sock: retval = self.sock.recv(1024)
        except socket.timeout, e:
            logging.debug("OVPN management socket operation timed-out: {0}".format(e.message))
            return None 
        except Exception as e:
            logging.exception("OVPN management socket error: ")
            return None
        finally:   # always execute
            try:
                if self.sock: self.sock.close()
                connected = False
                del self.sock
                self.sock = None # avoid exception of missing attribute in class
            except Exception, e:
                logging.warning("FATAL - closing the socket failed the next open operation would not work")
                raise

        return retval

    def hangup(self):
        """ notify hangup, force OpenVPN to reload its config """
        logging.debug("sending hangup signal")
        self.send("signal SIGHUP\n")
        self.connected = False

    def terminate(self):
        """ send termination signal, ask the OpenVPN client to stop """
        logging.debug("sending terminate signal")
        self.send("signal SIGTERM\n")
        self.connected = False

    def poll_status(self, last_known_gateway = None):
        """ 
        Open connection to management socket and query the current status of OpenVPN. There's an important
        step implemented in this method, which is the translation of what OpenVPN reports as it's current
        status and the actual status that viper reports as current. Sometimes OpenVPN can report a connected 
        state but further inspection of the routing table shows that it is not the case. The OpenVPN state
        is sotred in the dictionary as 'ovpn_state' and the status the viper reports is stored 'viper_status'.

        @param connection_timeout seconds that elapse before a socket.timeout exception is raised upon connection
        @param response_delay seconds to wait to get a response from the 'state' management command
        @return a dictionary with the current state of the connection stack, the one the client reports is identified by the key 'viper_status'
        """

        logging.debug("Polling OpenVPN for vpn status...")
        retval = {}
        resp = None

        try:
            # send state command and parse result back
            resp = self.parse_state_response( self.send("state\n") )

            if not resp:
                # if we didn't hear anything back from OpenVPN we keep trying for a few more loops
                if self.retries > 3:
                    retval['viper_status'] = "DISCONNECTED"
                    self.retries = 0
                else:
                    self.retries += 1
                    retval['viper_status'] = "TIMED-OUT"
                    logging.debug("No data received while waiting for response from OpenVPN")
            else:
                self.retries = 0 # reset retry counter

                retval = resp

                if resp['ovpn_state'] in ['CONNECTED']:
                    logging.debug("OpenVPN reports connected")
                    self.connected = True
                    retval['viper_status'] = "CONNECTED"

                    # we only get a new gateway if a CONNECTED, SUCCESS message was read
                    if ( ('gateway' in resp) and (self.cb_last_gateway)):
                        self.cb_last_gateway( resp['interface'] )
                    #     reactor.core.last_known_gateway = resp['interface'] #resp['gateway']
                elif resp['ovpn_state'] in ['ASSIGN_IP', 'AUTH', 'GET_CONFIG', 'RECONNECTING', 'ADD_ROUTES']:
                    self.connected = False
                    retval['viper_status'] = "CONNECTING"
                elif (resp['ovpn_state'] in ['WAIT']) and last_known_gateway:
                    # connection seems stuck, restart the connection if we ever knew a gateway
                    logging.debug("WAIT state detected, notifying SIGHUP")
                    self.hangup()
                    self.connected = False
                    retval['viper_status'] = "CONNECTING"
                elif resp['ovpn_state'] in ['WAIT']:
                    retval['viper_status'] = "DISCONNECTED"
                    self.connected = False
                # in any other case
                else:
                    retval['viper_status'] = "DISCONNECTED"
                    self.connected = False

        except Exception, e:
            logging.exception("Exception while polling for status: ")
            logging.warning(resp)
            retval['viper_status'] = "DISCONNECTED" 

        return retval


    def parse_state_response(self, msg):
        """ Parse OpenVPN management interface messages like this: 
                >INFO:OpenVPN Management Interface Version 1 -- type 'help' for more info
                1374575393,CONNECTED,SUCCESS,172.26.37.6,213.108.105.101
                END

            These are the OpenVPN states:
                CONNECTING    -- OpenVPN's initial state.
                WAIT          -- (Client only) Waiting for initial response
                                 from server.
                AUTH          -- (Client only) Authenticating with server.
                GET_CONFIG    -- (Client only) Downloading configuration options
                                 from server.
                ASSIGN_IP     -- Assigning IP address to virtual network
                                 interface.
                ADD_ROUTES    -- Adding routes to system.
                CONNECTED     -- Initialization Sequence Completed.
                RECONNECTING  -- A restart has occurred.
                EXITING       -- A graceful exit is in progress.

            source http://openvpn.net/index.php/open-source/documentation/miscellaneous/79-management-interface.html
        """
        if not msg:
            return None

        try:
            lines = string.split(msg, os.linesep)

            for l in lines:
                if '>' in l:
                    self.parse_realtime_msg(l)
                elif ',' in l:
                    # The output format consists of 5 comma-separated parameters: 
                    #   (a) the integer unix date/time,
                    #   (b) the state name,
                    #   (c) optional descriptive string (used mostly on RECONNECTING
                    #       and EXITING to show the reason for the disconnect),
                    #   (d) optional TUN/TAP local IP address (shown for ASSIGN_IP
                    #       and CONNECTED), and
                    #   (e) optional address of remote server (OpenVPN 2.1 or higher).                    
                    parts = string.split(l, ",")
                    if len(parts) < 5:
                        continue        # not what we are looking for, ignore

                    tstamp, state, desc, tun_ip, remote_ip = parts
                    logging.debug(parts)
                    
                    # get line containing status
                    if state == "CONNECTED" and desc == "SUCCESS":
                        return {'ovpn_state': "CONNECTED", 'interface' : tun_ip.split('\r')[0], 'gateway' : remote_ip}
                    # sometimes ovpn reports as connected but with errors    
                    elif state == "CONNECTED" and desc == "ERROR":
                        # e.g. Warning: route gateway is not reachable on any active network adapters: <ip address>
                        return {'ovpn_state': "DISCONNECTED"}
                    else:
                        return {'ovpn_state': state}
                else:
                    continue
        except Exception, e:
            logging.warning("Failed to parse status response: %s" % e)

    def parse_realtime_msg(self, line):
        """not yet supported"""
        pass
