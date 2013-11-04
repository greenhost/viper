#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Greenhost VOF and contributors
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.
#
"""
Polls status of OpenVPN using the management socket interface.
"""
import subprocess, logging
import os, sys, traceback
from datetime import datetime
import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os, sys, string, time
import socket
import threading, time
from pprint import pprint

from viper import routing 
from viper.tools import *
import traceback

class OVPNInterface:
    def __init__(self):
        self.connected = False
        self.sock = None
        self.last_known_gateway = None  # in this session, we don't save to disk between sessions

    def send(self, command, connection_timeout = 1, response_delay = .5):
        retval = None
        try:
            self.sock = socket.socket()
            logging.debug("Trying to connect to OVPN management socket")
            self.sock.settimeout( connection_timeout )
            self.sock.connect(("localhost", 7505))
            # sock.setblocking(1)
            self.connected = True

            logging.debug("Connected successfully to management socket")

            count = self.sock.send(command)
            if count == 0:
                logging.debug("Couldn't send message through socket")
            time.sleep( response_delay ) # must wait a bit otherwise we will not get a response to our request

            retval = self.sock.recv(1024)
        except socket.timeout, e:
            logging.debug("OVPN management socket operation timed-out: %s" % e)
            #retval = {'status': "DISCONNECTED"}
            return None 
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            logging.warning("OVPN management socket error: %s" % e)
            #retval = {'status': "DISCONNECTED"}
            return None
        finally:   # always execute
            try:
                self.sock.close()
                connected = False
                del self.sock
            except Exception, e:
                logging.warning("FATAL - closing the socket failed the next open operation would not work")
                raise

        return retval

    def hangup(self):
        """ notify hangup, force OpenVPN to reload its config """
        self.send("signal SIGHUP\n")
        self.connected = False

    def terminate(self):
        """ send termination signal, ask the OpenVPN client to stop """
        self.send("signal SIGTERM\n")
        self.connected = False

    def poll_status(self):
        """ 
        Open connection to management socket and query the current status of OpenVPN 
        @param connection_timeout seconds that elapse before a socket.timeout exception is raised upon connection
        @param response_delay seconds to wait to get a response from the 'state' management command
        """

        logging.debug("Polling OpenVPN for vpn status...")
        retval = None
        resp = None

        try:
            # send state command and parse result back
            resp = self.parse_state_response( self.send("state\n") )

            if not resp:
                retval = {'status': "DISCONNECTED"} 
                logging.debug("No data received while waiting for response from OpenVPN")
            else:
                retval = resp

                # always cross-check the routing with the last known gateway                    
                xcheckok = False
                if self.last_known_gateway:
                    try:
                        if not routing.verify_vpn_routing_table(self.last_known_gateway):
                            retval = {'status' : "DISCONNECTED"}
                            logging.debug("Routing verification didn't pass")
                        else:
                            xcheckok = True
                    except routing.InconsistentRoutingTable:
                        # @todo this error also comes up when we try to run OpenVON for a second time and we see that the routing tables are already set 
                        retval = {'status' : "INCONSISTENT"}
                        logging.debug("Routing verification is not consistent")

                if resp['state'] in ['CONNECTED']:
                    # OpenVPN says we are connected, don't believe it, verify cross-check
                    if xcheckok:
                        self.connected = True
                        retval = {'status' : "CONNECTED"}

                    # we only get a new gateway if a CONNECTED, SUCCESS message was read
                    if 'gateway' in resp:
                        self.last_known_gateway = resp['gateway']

                elif resp['state'] in ['ASSIGN_IP', 'AUTH', 'GET_CONFIG', 'RECONNECTING', 'ADD_ROUTES']:
                    self.connected = False
                    retval = {'status': "CONNECTING"}
                
                elif (resp['state'] in ['WAIT']) and (self.last_known_gateway):
                    # restart the connection if we ever knew a gateway
                    logging.debug("WAIT state detected, notifying SIGHUP")
                    self.hangup()
                    self.connected = False
                    retval = {'status': "CONNECTING"}
                elif (resp['state'] in ['WAIT']):
                    retval = {'status' : "DISCONNECTED"}
                    self.connected = False

        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            logging.warning("Exception while polling for status: %s" % e)
            pprint(resp)
            retval = {'status': "DISCONNECTED"} 

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
        if not msg: return None

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

                    # get line containing status
                    if state == "CONNECTED" and desc == "SUCCESS":
                        return {'state': "CONNECTED", 'interface' : tun_ip.split('\r')[0], 'gateway' : remote_ip}
                    # sometimes ovpn reports as connected but with errors    
                    elif state == "CONNECTED" and desc == "ERROR":
                        # e.g. Warning: route gateway is not reachable on any active network adapters: <ip address>
                        return {'state': "DISCONNECTED"}
                    else:
                        return {'state': state}
                else:
                    continue
        except Exception, e:
            logging.warning("Failed to parse status response: %s" % e)

    def parse_realtime_msg(self, line):
        """not yet supported"""
        pass
