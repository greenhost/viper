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
Launch & terminate the OpenVPN subprocess
"""
import subprocess
import os, sys, logging, string, time
from datetime import datetime
from pprint import pprint
import psutil

from viper import routing
from viper.windows import service
from viper.tools import *
from viper.openvpn import management
import traceback


class VPNLauncherException(Exception):
    pass

class OpenVPNNotFoundException(VPNLauncherException):
    pass


class OpenVPNLauncher:
    def __init__(self):
        self.proc = None

    def launch(self, cfgfile):
        """Start the OpenVPN process """
        path = get_openvpn_home()
        path = os.path.join(path, "openvpn")
        # logfile goes to user's AppData dir
        logfile = os.path.join(get_user_cwd(), "openvpn.log")

        cmd = "%s %s --log %s" % (path, cfgfile, logfile)
        logging.debug("Trying to execute OpenVPN client %s" % (cmd,))
        # @todo redirect stdout and stderr to /dev/null, perhaps we want to send this output somewhere else?
        f = open(os.devnull, 'w')
        try:
            self.proc = subprocess.Popen([path, cfgfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # @todo check return code (e.g. OpenVPN fails to start is the config file is malformed, Viper doesn't report that condition in any way yet)
            time.sleep(0.3)
            self.proc.poll()
            if self.proc.returncode:#   != 0:
                msg = "Executing external OpenVPN process failed returning %s" % (self.proc.returncode,)
                # log error and propagate condition
                logging.error(msg)
                raise VPNLauncherException(msg)
        except OSError, e:
            # @todo check if the exception above is actually raised by subprocess.Popen
            msg = "Couldn't execute subprocess '%s'" % (path,)
            # log and propagate
            logging.critical(msg)
            raise OpenVPNNotFoundException(msg)

    def terminate(self):
        """Terminate all OpenVPN processes that might be running"""
        logging.debug("Terminating OpenVPN subprocess")
        # terminate openvpn processes
        try:
            procs = is_openvpn_running()
            if procs: # process found, terminate it
                for p in procs:
                    p.terminate()  # NoSuchProcess: process no longer exists (pid=2476)
        except (psutil.NoSuchProcess, psutil.AccessDenied), err:
            logging.error("exception while trying to shut down OpenVPN process for pid:%s, reason:%s" % (err.pid, err.msg))
