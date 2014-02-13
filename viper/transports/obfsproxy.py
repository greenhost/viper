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
"""
obfsproxy and other pluggable transports
"""
import subprocess, logging, platform, os.path
import viper

obfs_supported_encodings = {'obfs2' : True, 'obfs3' : True}

def __build_arg_list(dest, dport, pport, transport="obfs3", shared_secret=None):
    """Build CLI parameter list for obfsproxy
        Args:
            dest (ip): destination ip
            dport (int): destination port
            pport (int): proxy port 
    """
    ssparam = ""
    if shared_secret:
        ssparam = " --shared-secret={0}".format(shared_secret)
    return " --log-file=obfsproxy.log {0} {1} --dest={2}:{3} client 127.0.0.1:{4}".format( transport, ssparam, dest, dport, pport )

def win32_start_obfsproxy(dest, dport, pport):
    args = __build_arg_list( dest, dport, pport ) 
    obfsproxyExe = "obfsproxy" + os.path.sep + "obfsproxy.exe"
    cmd = obfsproxyExe + args
    logging.debug(cmd)
    return subprocess.Popen(cmd.split(), **hide_window)

def darwin_start_obfsproxy(dest, dport, pport):
    args = __build_arg_list( dest, dport, pport ) 
    cmd = "./obfsproxy" + args
    logging.debug(cmd)
    return subprocess.Popen(cmd.split())

def linux_start_obfsproxy(dest, dport, pport):
    args = __build_arg_list( dest, dport, pport ) 
    cmd = "obfsproxy" + args
    logging.debug(cmd)
    return subprocess.Popen(cmd.split())

# ############################################################################
# Pluggable transports
# ############################################################################
class Transport:
    pass

class ObfsproxyTransport(Transport):
    """ This transport uses Tor's obfsproxy to steganographically encode OpenVPN traffic """

    def __init__(self, dest, dport, pport=10194):
        self.destination_addr = dest
        self.destination_port = dport
        self.proxy_port = pport
        self.process = None

    def start(self):
        if viper.IS_WIN:
            self.process = win32_start_obfsproxy( self.destination_addr, self.destination_port, self.proxy_port )
        elif viper.IS_OSX:
            self.process = darwin_start_obfsproxy( self.destination_addr, self.destination_port, self.proxy_port )
        else:
            self.process = linux_start_obfsproxy( self.destination_addr, self.destination_port, self.proxy_port )

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None

