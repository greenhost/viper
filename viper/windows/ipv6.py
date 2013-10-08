#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
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
Routines to enable and disable IPv6 and Windows technologies related to IPv6 stack such as TEREDO

@note these methods are not used. see firewall.py for details on 
how we block ipv6 traffic now.
"""
import subprocess, socket
import os, sys, logging, string, time

from viper.windows import *
import traceback
import socket

# (!!!) http://help.yahoo.com/l/nl/yahoo/ipv6/general/ipv6-10.html
#
# disable IPv6 according to http://social.technet.microsoft.com/Forums/windowsserver/en-US/c325f0b9-8315-49c6-9db6-a5e64559dc94/how-can-i-disable-ipv6-stack-in-core
# reg add hklm\system\currentcontrolset\services\tcpip6\parameters /v DisabledComponents /t REG_DWORD /d 255
#
# http://support.serverintellect.com/KB/a135/how-to-disable-ipv6-on-windows-server-2008.aspx
# Set http://support.serverintellect.com/KB/a135/how-to-disable-ipv6-on-windows-server-2008.aspx to 0xFFFFFFFF
#
#
#   
# os.system is a very old choice and not really recommended.
#
# Instead you should consider subprocess.call() or subprocess.Popen().
#
# Here is how to use them:
#
# If you don't care about the output, then:
#
# import subprocess
# ...
# subprocess.call('netsh interface ipv4 set interface ""Wireless Network" metric=1', shell=True)
# If you do care about the output, then:
#
# netshcmd=subprocess.Popen('netsh interface ipv4 set interface ""Wireless Network" metric=1', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
# output, errors =  netshcmd.communicate()
# if errors: 
#    print "WARNING: ", errors
#  else:
#    print "SUCCESS ", output

COMMAND = {
    "enable": "netsh interface teredo set state type=default",
    "disable" : [
            "netsh interface teredo set state disabled",
            "netsh interface 6to4 set state disabled",
            "netsh interface isatap set state disabled",
            ],
}

class DeviceSwitchingException(Exception):
    pass

class TeredoCapabilityException(DeviceSwitchingException):
    pass


def has_ipv6_support():
    """Check if we can open an IPv6 socket, if we can that means that
    the current machine supports the IPv6 stack."""
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        return True
    except:
        return False

def ipv6_disable():
    """Disable the IPv6 stack on Windows 7 & 8 
    @note requires reboot to take effect"""
    try:
        self.proc = subprocess.Popen('reg add hklm\\system\\currentcontrolset\\services\\tcpip6\\parameters /v DisabledComponents /t REG_DWORD /d 255', 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.proc.wait()
        if self.proc.returncode:
            msg = "Disabling IPv6 didn't return the expected value (return code = {0})".fomat(self.proc.returncode,)
            logging.warning( msg )
            raise TeredoCapabilityException( msg )
    except OSError, e:
        msg = "Couldn't execute the command to disable IPv6"
        # log and propagate
        logging.error(msg)
        raise TeredoCapabilityException(msg)

def ipv6_enable():
    """Enable the IPv6 stack on Windows 7 & 8 
    @note requires reboot to take effect"""
    try:
        self.proc = subprocess.Popen('reg delete hklm\\system\\currentcontrolset\\services\\tcpip6\\parameters /f', 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.proc.wait()
        if self.proc.returncode:
            msg = "Enabling IPv6 didn't return the expected value (return code = {0})".format(self.proc.returncode,)
            logging.warning( msg )
            raise TeredoCapabilityException( msg )
    except OSError, e:
        msg = "Couldn't execute the command to enable IPv6"
        # log and propagate
        logging.error(msg)
        raise TeredoCapabilityException(msg)

def teredo_enable():
    """Enable TEREDO IPv6 tunneling"""
    try:
        for cmd in COMMAND['enable']:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.proc.wait()
            if self.proc.returncode:
                msg = "Enabling TEREDO back again didn't return the expected value (return code = {0})".format(self.proc.returncode,)
                logging.warning( msg )
                raise TeredoCapabilityException( msg )
    except OSError, e:
        msg = "Couldn't execute the command to enable TEREDO"
        # log and propagate
        logging.error(msg)
        raise TeredoCapabilityException(msg)

def teredo_disable():
    """Disable TEREDO IPv6 tunneling"""
    try:
        for cmd in COMMAND['disable']:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.proc.wait()
            if self.proc.returncode:
                msg = "Disabling TEREDO didn't return the expected value (return code = {0})".format(self.proc.returncode,)
                logging.warning( msg )
                raise TeredoCapabilityException( msg )
    except OSError, e:
        msg = "Couldn't execute the command to disable TEREDO"
        # log and propagate
        logging.critical(msg)
        raise TeredoCapabilityException(msg)
