#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re
import threading, time, traceback, string
from pprint import pprint
import logging
import getopt
import atexit
import json
from viper.backend import http

def on_exit():
    logging.info("I'm leaving. Bye.")

if __name__ == '__main__':
    atexit.register( on_exit )
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG, filemode="w+")
    http.serve(debug=True)
