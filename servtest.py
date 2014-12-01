
from viper import routing
from viper.windows import service
from viper.openvpn import monitor
from viper.tools import *
import traceback

def start():
	from rpyc.utils.server import ThreadedServer
    logging.info("OVPN START...")
	# make sure only connections from localhost are accepted
	self.svc = ThreadedServer(monitor.RPCService, hostname = 'localhost', port = 18861)

def stop():
    logging.info("OVPN STOP...")
    self.svc.close()

if __name__ == '__main__':
	#log_init_service()
	logging.basicConfig(level=logging.DEBUG)
	start()
