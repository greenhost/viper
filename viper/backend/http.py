#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import os, sys, re
# import threading, time, traceback, string
# import getopt
# import atexit
import json
import logging
import os

try:
    from viper.backend import bottle
except ImportError, e:
    logging.exception("Failed to import Bottle module from HTTP controller")

try:
    from viper.backend.bottle import route, template, get, post, request
except ImportError, e:
    logging.exception("Failed to import Bottle routines into current namespace")

from viper import policies
from viper import tools

try:
    from viper import reactor
except ImportError, e:
    logging.exception("Failed to import reactor from http controller")

## MODULE GLOBALS ###########################################################
vstate = "DISCONNECTED"
httpserver = None

def get_view_path():
    """
    Find path to html templates for Viper service
    :return: full path to the views directory
    """
    return os.path.join(tools.get_viper_home(), './resources/www/views')

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
    #pprint(request.body)
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


## ###########################################################################
class EmbeddedServer(bottle.ServerAdapter):
    """ Bottle-specific HTTP server wrapper """
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        else:
            class LoggerHandler(WSGIRequestHandler):
                def log_request(*args, **kw):
                    logging.debug("EbeddedServer - received request")
            self.options['handler_class'] = LoggerHandler

        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

## ###########################################################################
def init(debug=True):
    """ Configure the HTTP server """
    logging.debug("Initializing the http backend...")
    bottle.debug(debug)
    bottle.TEMPLATES.clear()  # clear template cache
    vpath = get_view_path()
    logging.debug( "Setting template path to {0}".format(vpath) )
    bottle.TEMPLATE_PATH.insert(0, vpath)

def serve(host='127.0.0.1', port=8088):
    """ Start the HTTP server loop """
    global httpserver
    # bottle.run(host=host, port=port)
    app = bottle.default_app()
    httpserver = EmbeddedServer(host=host, port=port)
    try:
        app.run(server=httpserver)
    except Exception as ex:
        logging.exception("HTTP server encountered an error")

def shutdown():
    """ Shut the HTTP server down """
    global httpserver
    logging.info()
    httpserver.stop()

"""
Another example: https://github.com/pacopablo/bottle-nt-service/blob/master/bottle_service.py
See for sample server impl: http://stackoverflow.com/questions/11282218/bottle-web-framework-how-to-stop
"""
