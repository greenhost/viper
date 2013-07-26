#!/usr/bin/env python
import os, sys
import logging
import servicemanager
import appdirs

try:
    import psutil
except ImportError:
    print("psutil module is required for process tracking. Please see: https://code.google.com/p/psutil/")

## logging
# import logging
# from logging.handlers import NTEventLogHandler
# logger = logging.getLogger("test")
# wh = NTEventLogHandler("test")

# logger.addHandler(wh)
# logger.setLevel(logging.INFO)
# logger.info("This is just a test")

# if "python.exe" in sys.executable:
#     use print
# else:
#     use logging



# useful globals
PRODUCT_NAME = "UmanViper"
PRODUCER_NAME = "Greenhost"
DEFAULT_OPENVPN_HOME = "./openvpn/"

def is_openvpn_running():
    procs = [p for p in psutil.get_process_list() if 'openvpn' in p.name]
    return procs

def log_init():
	logging.basicConfig(filename='ovpnmon.log',level=logging.DEBUG)

def get_openvpn_home():
	return os.getenv('OPENVPN_HOME', DEFAULT_OPENVPN_HOME)

def get_my_cwd():
	return os.path.dirname(sys.executable)

def get_user_cwd():
	d = appdirs.AppDirs(PRODUCT_NAME, PRODUCER_NAME)
	
	if not os.path.exists(d.user_data_dir):
		os.makedirs(d.user_data_dir)

	return d.user_data_dir

def log(msg):
	servicemanager.LogInfoMsg(str(msg))
	#print(msg)


def _windows_has_tap_device():
    """
    Loops over the windows registry trying to find if the tap0901 tap driver
    has been installed on this machine.
    """
    import _winreg as reg

    adapter_key = 'SYSTEM\CurrentControlSet\Control\Class' \
        '\{4D36E972-E325-11CE-BFC1-08002BE10318}'
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, adapter_key) as adapters:
        try:
            for i in xrange(10000):
                key_name = reg.EnumKey(adapters, i)
                with reg.OpenKey(adapters, key_name) as adapter:
                    try:
                        component_id = reg.QueryValueEx(adapter,
                                                        'ComponentId')[0]
                        if component_id.startswith("tap0901"):
                            return True
                    except WindowsError:
                        pass
        except WindowsError:
            pass
    return False


# def WindowsInitializer():
#     """
#     Raises a dialog in case that the windows tap driver has not been found
#     in the registry, asking the user for permission to install the driver
#     """
#     if not _windows_has_tap_device():
#         msg = QtGui.QMessageBox()
#         msg.setWindowTitle(msg.tr("TAP Driver"))
#         msg.setText(msg.tr("LEAPClient needs to install the necessary drivers "
#                            "for Encrypted Internet to work. Would you like to "
#                            "proceed?"))
#         msg.setInformativeText(msg.tr("Encrypted Internet uses VPN, which "
#                                       "needs a TAP device installed and none "
#                                       "has been found. This will ask for "
#                                       "administrative privileges."))
#         msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
#         msg.setDefaultButton(QtGui.QMessageBox.Yes)
#         ret = msg.exec_()

#         if ret == QtGui.QMessageBox.Yes:
#             # XXX should do this only if executed inside bundle.
#             # Let's assume it's the only way it's gonna be executed under win
#             # by now.
#             driver_path = os.path.join(os.getcwd(),
#                                        "apps",
#                                        "eip",
#                                        "tap_driver")
#             dev_installer = os.path.join(driver_path,
#                                          "devcon.exe")
#             if os.path.isfile(dev_installer) and \
#                     stat.S_IXUSR & os.stat(dev_installer)[stat.ST_MODE] != 0:
#                 inf_path = os.path.join(driver_path,
#                                         "OemWin2k.inf")
#                 cmd = [dev_installer, "install", inf_path, "tap0901"]
#                 ret = subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
#             else:
#                 logger.error("Tried to install TAP driver, but the installer "
#                              "is not found or not executable")

