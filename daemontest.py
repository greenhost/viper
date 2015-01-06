#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import atexit
from viper.backend import http

def on_exit():
    logging.info("I'm leaving. Bye.")

if __name__ == '__main__':
    logging.getLogger('').handlers = []   # clear any existing log handers
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG)
    atexit.register( on_exit )

    http.init(debug=True)
    http.serve(host='127.0.0.1', port=8088)
