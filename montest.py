#!/usr/bin/env python


import os, sys, re, time
import logging
from pprint import pprint
import viper
from viper.openvpn import management, launcher
from viper import tools


def main():
	logging.basicConfig(level=logging.DEBUG)
	man = management.OVPNInterface()
	while True:
		status = man.poll_status()
		pprint(status)
		time.sleep(0.2)


if __name__ == '__main__':
	main()