import os
import logging
import json
from viper.backend.bottle import Bottle, route, template, get, post, request
from viper.backend import bottle
from viper import policies
from viper import tools
from viper import reactor

## MODULE GLOBALS ###########################################################
vstate = "DISCONNECTED"
#httpserver = None
__app__ = Bottle()


def get_view_path():
    """
    Find path to html templates for Viper service
    :return: full path to the views directory
    """
    return os.path.join(tools.get_viper_home(), './resources/www/views')

def init(debug=True):
    """ Initialize logging and HTTP engine """
    logging.getLogger('').handlers = [] # clear any existing log handlers
    logging.basicConfig(filename="c:/ovpnmon.log", level=logging.DEBUG, filemode="w+")

    bottle.TEMPLATES.clear()  # clear template cache
    vpath = get_view_path()
    logging.debug( "Setting template path to {0}".format(vpath) )
    bottle.TEMPLATE_PATH.insert(0, vpath)

@__app__.route('/hello')
def hello():
    return "Hello World."

## Request handlers
@__app__.route('/', method='GET')
def home():
    return bottle.template('index', title="Viper dashboard")

@__app__.route('/resources/<filename>')
def server_static(filename):
    root = os.path.join(os.environ.get('VIPER_HOME'), 'resources/www/res/')
    logging.info("Requesting resource {0} in {1}".format(filename, root) )
    logging.info("VIPER_HOME={0}".format(os.environ.get('VIPER_HOME')) )
    return bottle.static_file(filename, root=root)

@__app__.route('/tunnel/open', method='POST')
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
        logging.debug("Content-type: ".format(request.content_type))
        r = request.body.readlines()
        logging.debug( "Request didn't contain the expected parameters {0}".format(r) )
        raise bottle.HTTPResponse(output='Failed to initialize tunnel', status=503, header=None)

@__app__.route('/tunnel/close', method='POST')
def req_tunnel_close():
    logging.info("Closing tunnel")
    reactor.core.tunnel_close()

@__app__.route('/tunnel/status', method='GET')
def req_tunnel_status():
    global vstate
    state = {"state" : vstate, "policies" : ["ipv6", "xcheck", "gatewaymon"]}
    return json.dumps( state )

@__app__.route('/policy', method=['GET','OPTIONS'])
def req_policy():
    logging.info( "Request to policy, method = {0}".format(request.method) )
    if request.method == "GET":
        logging.info( "Getting list of policies that this daemon implements" )
        return json.dumps( policies.POLICIES_SUPPORTED.keys() )
    elif request.method == "OPTIONS":
        logging.info( "Getting currently active policies" )
        return json.dumps( policies.get_active_policies() )

@__app__.route('/policy/enable', method='POST')
def req_policy_enable():
    jreq = request.json
    #pprint(request.body)
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policies.policy_enable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to enable policy', status=503, header=None)

@__app__.route('/policy/setting', method=['GET', 'POST'])
def req_policy_setting():
    pass

@__app__.route('/policy/disable', method='POST')
def req_policy_disable():
    jreq = request.json
    if jreq and ('name' in jreq):
        logging.info( "Request to enable policy with name [{0}]".format(jreq['name']) )
        policies.policy_disable(jreq['name'])
    else:
        raise bottle.HTTPResponse(output='Failed to disable policy', status=503, header=None)

