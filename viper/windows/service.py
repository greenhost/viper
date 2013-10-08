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
Install and autostart a ser vice on windows.
"""
## {{{ http://code.activestate.com/recipes/551780/ (r3)
# winservice.py

from os.path import splitext, abspath
from sys import modules

import win32serviceutil
import win32service
import win32event
import win32api
import viper.openvpn
import psutil

# a post on the installer
# http://www.islascruz.org/html/?gadget=StaticPage&action=Page&id=6
def instart(cls, name, display_name=None, stay_alive=True):
    ''' Install and  Start (auto) a Service
            
        cls : the class (derived from Service) that implement the Service
        name : Service name
        display_name : the name displayed in the service manager
        stay_alive : Service will stop on logout if False
    '''
    cls._svc_name_ = name
    cls._svc_display_name_ = display_name or name
    try:
        module_path=modules[cls.__module__].__file__
    except AttributeError:
        # maybe py2exe went by
        from sys import executable
        module_path=executable
    module_file = splitext(abspath(module_path))[0]
    cls._svc_reg_class_ = '%s.%s' % (module_file, cls.__name__)
    if stay_alive: win32api.SetConsoleCtrlHandler(lambda x: True, True)
    try:
        win32serviceutil.InstallService(
            cls._svc_reg_class_,
            cls._svc_name_,
            cls._svc_display_name_,
            startType = win32service.SERVICE_AUTO_START
        )
        print 'Install ok'
        win32serviceutil.StartService(
            cls._svc_name_
        )
        print 'Start ok'
    except Exception, x:
        print str(x)

