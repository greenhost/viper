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
Launch & terminate the OpenVPN subprocess
"""
import subprocess
import os, sys, logging, string, time
import shlex
from datetime import datetime
from pprint import pprint
import psutil

from viper import routing
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

    def launch(self, cfgfile, logdir):
        """Start the OpenVPN process """
        path = get_openvpn_home()
        path = os.path.join(path, "openvpn")
        # logfile goes to user's AppData dir
        logfile = os.path.join(logdir, "openvpn.log")

        cmd = "{0} --config {1} --log {2}".format(path, cfgfile, logfile)
        logging.debug("Trying to execute OpenVPN client %s" % (cmd,))
        # @todo redirect stdout and stderr to /dev/null, perhaps we want to send this output somewhere else?
        f = open(os.devnull, 'w')
        try:
            # prepare argument list for Popen
            args = [path, "--config", cfgfile, "--log", logfile]
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            time.sleep(0.3)
            self.proc.poll()
            if self.proc.returncode:#   != 0:
                msg = "Executing external OpenVPN process failed returning %s" % (self.proc.returncode,)
                # log error and propagate condition
                logging.error(msg)
                raise VPNLauncherException(msg)
            # return pid on successful run
            return self.proc.pid
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
