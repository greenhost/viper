#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
#
# Copyright (C) 2013 Greenhost vof
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
        path = get_openvpn_home()
        path = os.path.join(path, "openvpn")

        cmd = "%s %s" % (path, cfgfile)
        logging.debug("Trying to execute OpenVPN client %s" % (cmd,))
        # @todo redirect stdout and stderr to /dev/null, perhaps we want to send this output somewhere else?
        f = open(os.devnull, 'w')
        try:
            self.proc = subprocess.Popen([path, cfgfile], stdout=f, stderr=f)
            # @todo check return code (e.g. OpenVPN fails to start is the config file is malformed, Viper doesn't report that condition in any way yet)
            logging.debug("OpenVPN process returned exit code = %s" % (self.proc.returncode,) )
            if self.proc.returncode != 0:
                msg = "Executing external OpenVPN process failed returning %s" % (self.proc.returncode,)
                # log error and propagate condition
                logging.error(msg)
                raise VPNLauncherException(msg)
        except EnvironmentError, e:
            # @todo check if the exception above is actually raised by subprocess.Popen
            msg = "Couldn't execute subprocess '%s'" % (path,)
            # log and propagate
            logging.critical(msg)
            raise OpenVPNNotFoundException(msg)

    def terminate(self):
        logging.debug("Terminating OpenVPN subprocess")
        # terminate openvpn processes
        try:
            procs = is_openvpn_running()
            if procs: # process found, terminate it
                for p in procs:
                    p.terminate()  # NoSuchProcess: process no longer exists (pid=2476)
        except (psutil.NoSuchProcess, psutil.AccessDenied), err:
            logging.error("exception while trying to shut down OpenVPN process for pid:%s, reason:%s" % (err.pid, err.msg))
