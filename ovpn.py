#!/usr/bin/env python
__DOC__ = """ 
Helper code for OpenVPN status on windows
(c) Luis Rodil-Fernandez <luis@greenhost.nl>
"""
import subprocess
import os, sys
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

import win.routing
import win.tools
from win.tools import log
import traceback



def poll_status(self, connection_timeout = 2, response_delay = .5):
    """ 
    Open connection to management socket and query the current status of OpenVPN 
    @param connection_timeout seconds that elapse before a socket.timeout exception is raised upon connection
    @param response_delay seconds to wait to get a response from the 'state' management command
    """

    log("Polling OpenVPN for vpn status...")
    retval = None
    sock = socket.socket()

    try:
        log("Trying to connect to OVPN management socket")
        sock.settimeout( connection_timeout )
        sock.connect(("localhost", 7505))
        # self.sock.setblocking(1)
        self.connected = True

        log("Connected successfully to management socket")

        sock.send("state\n")
        time.sleep( response_delay ) # must wait a bit otherwise we will not get a response to our request

        data = sock.recv(1024)

        if not data:
            retval = {'status': "DISCONNECTED"} 
            log("No data received while reading socket")
        else:
            log("RECV raw: %s" % (data,) )
            resp = self.parse_status_response(data)
            #pprint(OVPN_STATUS)
            # compare status with routing table
            if resp:
                retval = resp

                # verify that the routing table matches status readings
                if retval['status'] == "CONNECTED":
                    try:
                        if not routing.verify_vpn_routing_table(retval['gateway']):
                            retval = {'status' : "DISCONNECTED"}
                            log("Routing verification didn't pass")
                    except routing.InconsistentRoutingTable:
                        retval = {'status' : "INCONSISTENT"}
                        log("Routing verification is not consistent")

            else:
                retval = {'status' : "DISCONNECTED"}

    except socket.timeout, e:
        log("OVPN management socket operation timed-out: %s" % e)
        retval = {'status': "DISCONNECTED"} 
    except Exception, e:
        log("OVPN management socket error: %s" % e)
        retval = {'status': "DISCONNECTED"} 
    finally:   # always execute
        try:
            sock.close()
            self.connected = False
            del sock
        except Exception, e:
            log("FATAL - closing the socket failed the next open operation would not work")
            raise

    return retval


def parse_status_response(self, msg):
    """ Parse OpenVPN management interface messages like this: 
            >INFO:OpenVPN Management Interface Version 1 -- type 'help' for more info
            1374575393,CONNECTED,SUCCESS,172.26.37.6,213.108.105.101
            END
    """
    try:
        lines = string.split(msg, os.linesep)

        for l in lines:
            if ',' in l:
                parts = string.split(l, ",")

                # get line containing status
                if parts[1] == "CONNECTED" and parts[2] == "SUCCESS":
                    return {'status': "CONNECTED", 'interface' : parts[4].split('\r')[0], 'gateway' : parts[3]}
                elif parts[1] == "ASSIGN_IP":
                    return {'status': "CONNECTING"}
                else:
                    return None
            else:
                continue
    except Exception, e:
        log("Failed to parse status response: %s" % e)
