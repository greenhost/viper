#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
