#
# @license
#
# @todo what version of windows are we running?
# @todo how do we stop Teredo on that version of Windows?
# @todo how do we check if the network is up?
# @todo how to take down the network?
# @todo can we programmatically manipulate the firewall?
import viper
import platform

VERSION = None

if viper.IS_WIN:
	# get windows version
	VERSION = platform.win32_ver()[0]
