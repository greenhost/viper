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


def __build_arg_list(port):
    return " --log-file=obfsproxy.log obfs2 socks 127.0.0.1:{0}".format( port )

def win32_start_obfsproxy(port):
    args = __build_arg_list( port ) 
    obfsproxyExe = "obfsproxy" + os.path.sep + "obfsproxy.exe"
    cmd = obfsproxyExe + args
    return subprocess.Popen(cmd.split(), **hide_window)

def darwin_start_obfsproxy(port):
    args = __build_arg_list( port ) 
    cmd = "./obfsproxy" + args
    return subprocess.Popen(cmd.split())

def linux_start_obfsproxy(port):
    args = __build_arg_list( port ) 
    cmd = "obfsproxy" + args
    return subprocess.Popen(cmd.split())

# ############################################################################
# Pluggable transports
# ############################################################################
class Transport:
    pass

class ObfsproxyTransport(Transport):
    """ This transport uses Tor's obfsproxy to steganographically encode OpenVPN traffic """

    def __init__(self, socks_port=10194):
        self.proxy_port = socks_port
        self.process = None

    def start(self):
        if viper.IS_WIN:
            self.process = win32_start_obfsproxy( self.proxy_port )
        elif viper.IS_OSX:
            self.process = darwin_start_obfsproxy( self.proxy_port )
        else:
            self.process = linux_start_obfsproxy( self.proxy_port )

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def socks_port(self):
        return self.proxy_port

