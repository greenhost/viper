__author__ = 'pacopablo'

import os
import logging
import json
from viper.backend.bottle import Bottle, route, template, get, post, request
from viper.backend import bottle
from viper import policies
from viper import tools
from viper import reactor

logging.getLogger('').handlers = [] # clear any existing log handlers
logging.basicConfig(filename="c:/ovpnmon.log", level=logging.DEBUG, filemode="w+")

app = Bottle()

## MODULE GLOBALS ###########################################################
vstate = "DISCONNECTED"
httpserver = None

def get_view_path():
    """
    Find path to html templates for Viper service
    :return: full path to the views directory
    """
    return os.path.join(os.environ.get('VIPER_HOME'), './resources/www/views')

bottle.TEMPLATES.clear()  # clear template cache
vpath = get_view_path()
# logging.debug( "Setting template path to {0}".format(vpath) )
bottle.TEMPLATE_PATH.insert(0, vpath)

@app.route('/hello')
def hello():
    return "Hello World."

## Request handlers
@app.route('/', method='GET')
def home():
    return bottle.template('index', title="Viper dashboard")

@app.route('/resources/<filename>')
def server_static(filename):
    root = os.path.join(os.environ.get('VIPER_HOME'), './resources/www/res/')
    logging.info("Requesting %s in %s" %(filename, root))
    logging.info("VIPER_HOME: %s" %os.environ.get('VIPER_HOME'))
    return bottle.static_file(filename, root=root)

@app.route('/tunnel/open', method='POST')
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

@app.route('/tunnel/close', method='POST')
def req_tunnel_close():
    logging.info("Closing tunnel")
    reactor.core.tunnel_close()

@app.route('/tunnel/status', method='GET')
def req_tunnel_status():
    global vstate
    state = {"state" : vstate, "policies" : ["ipv6", "xcheck", "gatewaymon"]}
    return json.dumps( state )

@app.route('/policy', method=['GET','OPTIONS'])
def req_policy():
    logging.info( "Request to policy, method = {0}".format(request.method) )
    if request.method == "GET":
        logging.info( "Getting list of policies that this daemon implements" )
        return json.dumps( policies.POLICIES_SUPPORTED.keys() )
    elif request.method == "OPTIONS":
        logging.info( "Getting currently active policies" )
        return json.dumps( policies.get_active_policies() )

@app.route('/policy/enable', method='POST')
def req_policy_enable():
    jreq = request.json
    #pprint(request.body)
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policies.policy_enable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to enable policy', status=503, header=None)

@app.route('/policy/setting', method=['GET', 'POST'])
def req_policy_setting():
    pass

@app.route('/policy/disable', method='POST')
def req_policy_disable():
    jreq = request.json
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policies.policy_disable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to disable policy', status=503, header=None)

