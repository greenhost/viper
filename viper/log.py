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
Stream object that redirects writes to a logger instance.
"""
import logging

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.

    Credits to:
    http://www.electricmonk.nl/log/2011/08/14/\
        redirect-stdout-and-stderr-to-a-logger-in-python/
    """
    def __init__(self, logger, log_level=logging.INFO):
        """
        Constructor, defines the logger and level to use to log messages.

        :param logger: logger object to log messages.
        :type logger: logging.Handler
        :param log_level: the level to use to log messages through the logger.
        :type log_level: int
                        look at logging-levels in 'logging' docs.
        """
        self._logger = logger
        self._log_level = log_level

    def write(self, data):
        """
        Simulates the 'write' method in a file object.
        It writes the data receibed in buf to the logger 'self._logger'.

        :param data: data to write to the 'file'
        :type data: str
        """
        for line in data.rstrip().splitlines():
            self._logger.log(self._log_level, line.rstrip())

    def flush(self):
        """
        Dummy method. Needed to replace the twisted.log output.
        """
        pass


def replace_stdout_stderr_with_logging(logger):
    """
    Replace standard output and standard error streams
    with a custom handler that writes to the python logger.
    """
    sys.stdout = StreamToLogger(logger, logging.DEBUG)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
