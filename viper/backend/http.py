#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import os, sys, re
# import threading, time, traceback, string
# import getopt
# import atexit

import bottle
from bottle import route, template, get, post, request
import logging
import json
from pprint import pprint

from viper.backend.http import *
from viper import policies
from viper import reactor

vstate = "DISCONNECTED"
VIEWS_ROOT = './resources/www/views'

## ##########################################################################
## monitoring loop
## ##########################################################################
def start_monitor():
    global vstate
    vstate = 'CONNECTED'
    logging.info("Creating thread that checks connection status...")

def stop_monitor():
    global vstate
    vstate = 'DISCONNECTED'
    logging.info("Stopping thread that checks connection status...")

def handle_quit():
    quitting = True
    stop_monitor()
    logging.info('Bye, then.')

def on_exit():
    """ exit handler takes care of restoring firewall state """
    logging.info("Shutting down: closing everything")


## Request handlers
@route('/', method='GET')
def home():
    return bottle.template('index', title="Viper dashboard")

@route('/resources/<filename>')
def server_static(filename):
    return bottle.static_file(filename, root='resources/www/res/')

@route('/tunnel/open', method='POST')
def req_tunnel_open():
    logging.info("Request received to open tunnel")
    jreq = request.json
    #pprint(request.body)
    if jreq and ( ('config' in jreq) and ('log' in jreq) ):
        logging.debug( "Open tunnel wih params [config = {0}] [log = {1}]".format(jreq['config'], jreq['log']) )
        try:
            reactor.core.tunnel_open(jreq['config'], jreq['log'])
        except Exception, e:
            raise bottle.HTTPResponse(output='Failed to initialize tunnel', status=503, header=None)
    else:
        raise bottle.HTTPResponse(output='Failed to initialize tunnel', status=503, header=None)

@route('/tunnel/close', method='POST')
def req_tunnel_close():
    logging.info("Closing tunnel")
    reactor.core.tunnel_close()

@route('/tunnel/status', method='GET')
def req_tunnel_status():
    global vstate
    state = {"state" : vstate, "policies" : ["ipv6", "xcheck", "gatewaymon"]}
    return json.dumps( state )

@route('/policy', method=['GET','OPTIONS'])
def req_policy():
    logging.info( "Request to policy, method = {0}".format(request.method) )
    if request.method == "GET":
        logging.info( "Getting list of policies that this daemon implements" )
        return json.dumps( policies.POLICIES_SUPPORTED.keys() )
    elif request.method == "OPTIONS":
        logging.info( "Getting currently active policies" )
        return json.dumps( policies.get_active_policies() )

@route('/policy/enable', method='POST')
def req_policy_enable():
    jreq = request.json
    pprint(request.body)
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policies.policy_enable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to enable policy', status=503, header=None)

@route('/policy/setting', method=['GET', 'POST'])
def req_policy_setting():
    pass

@route('/policy/disable', method='POST')
def req_policy_disable():
    jreq = request.json
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policies.policy_disable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to disable policy', status=503, header=None)


def init(debug=True):
    """ start the http service loop """
    logging.debug("Initializing the http backend...")
    bottle.debug(debug)
    bottle.TEMPLATES.clear()  # clear template cache
    logging.debug("Setting template path to {0}".format(VIEWS_ROOT))
    bottle.TEMPLATE_PATH.insert(0, VIEWS_ROOT)

def serve(host='127.0.0.1', port=8088):
    bottle.run(host=host, port=port)


"""
From: http://stackoverflow.com/questions/11282218/bottle-web-framework-how-to-stop


from bottle import Bottle, ServerAdapter

class MyWSGIRefServer(ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()

app = Bottle()
server = MyWSGIRefServer(host=listen_addr, port=listen_port)
try:
    app.run(server=server)
except Exception,ex:
    print ex

When I want to stop the bottle application, from another thread, I do the following:

server.stop()
"""
