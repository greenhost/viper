#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re
import threading, time, traceback, string
from pprint import pprint
import bottle
from bottle import route, template, get, post, request
import logging
import getopt
import atexit
import json
from viper.backend.http import *
from viper.policies import *
from viper import reactor

vstate = "DISCONNECTED"

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
def tunnel_open():
    logging.info("Request received to open tunnel")
    jreq = request.json
    #pprint(request.body)
    if jreq and ( ('config' in jreq) and ('log' in jreq) ):
        logging.info( "Open tunnel wih params [config = {0}] [log = {1}]".format(jreq['config'], jreq['log']) )
        reactor.core.tunnel_open(jreq['config'], jreq['log'])
    else:
        raise bottle.HTTPResponse(output='Failed to enable policy', status=503, header=None)

@route('/tunnel/close', method='POST')
def tunnel_close():
    logging.info("Closing tunnel")
    reactor.core.tunnel_close()

@route('/tunnel/status', method='GET')
def tunnel_status():
    global vstate
    state = {"state" : vstate, "policies" : ["ipv6", "xcheck", "gatewaymon"]}
    return json.dumps( state )

@route('/policy', method=['GET','OPTIONS'])
def policy():
    logging.info( "Request to policy, method = {0}".format(request.method) )
    if request.method == "GET":
        logging.info( "Getting list of policies that this daemon implements" )
        return json.dumps( POLICIES_SUPPORTED.keys() )
    elif request.method == "OPTIONS":
        logging.info( "Getting currently active policies" )
        return json.dumps( get_active_policies() )

@route('/policy/enable', method='POST')
def policy_enable():
    jreq = request.json
    pprint(request.body)
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policy_enable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to enable policy', status=503, header=None)

@route('/policy/setting', method=['GET', 'POST'])
def policy_setting():
    pass

@route('/policy/disable', method='POST')
def policy_disable():
    jreq = request.json
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policy_disable(jreq['name'])
    else:
        raise HTTPResponse(output='Failed to disable policy', status=503, header=None)


def serve(host='127.0.0.1', port=8088, debug=True):
    """ start the http service loop """
    bottle.debug(debug)
    bottle.TEMPLATES.clear()  # clear template cache
    bottle.TEMPLATE_PATH.insert(0, './resources/www/views')
    bottle.run(host=host, port=port)
