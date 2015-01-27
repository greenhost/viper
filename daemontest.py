#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import atexit
from threading import Thread, Event
from viper.backend import http
import ovpnmon

def on_exit():
    logging.info("I'm leaving. Bye.")

if __name__ == '__main__':
    logging.getLogger('').handlers = []   # clear any existing log handers
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S', level=logging.DEBUG)
    atexit.register( on_exit )
    thread_event = Event()
    thread_event.set()

    http.init(debug=True)
    bottle_srv = ovpnmon.BottleWsgiServer(thread_event)
    bottle_srv.start()
