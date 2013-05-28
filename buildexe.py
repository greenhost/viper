#!/usr/bin/env python
## Win32 EXE Builder using PyInstaller 2.0
## Luis Rodil-Fernandez <luis@greenhost.nl>
##
## As of pyinstaller 2 there's no need for the 2-step process
## executables can now be build in a single call:
##
## $ python pyinstaller.py [opts] yourprogram.py
## 
## see documentation for further details: 
## http://www.pyinstaller.org/export/v2.0/project/doc/Manual.html?format=raw
import os, sys
import time, string
import subprocess
import shutil

PYINST_DEFAULT_PATH = 'C:\pyinstaller-2.0'

# Apps to build, specifying the entry point script and the icon to 
# embed in the executable file as a resource
APPS = [
		{'script': 'winservice.py', 'icon' : 'monitor.ico'},
		{'script': 'umanager.py', 'icon': 'online.ico'}
	   ]

# PyInstaller options
OPTS = ['--onefile', '--noconsole']

# Additional application resources
RES  = ['__config.ovpn', 'online.ico', 'offline.ico', 'README']

# relative to the CWD
def get_build_path():
	return os.path.join(os.getcwd(), "dist")

# absolute path to PyInstaller - expects an environment variable pointing to it
def get_pyinstaller_path():
	p = os.getenv("PYINSTALLER_HOME")
	if p:
		return p
	else:
		return PYINST_DEFAULT_PATH

# build actual command call to PyInstaller
def create_executables():
	print("Creating executables...")
	path = get_pyinstaller_path()
	cmd = os.path.join(path, "pyinstaller.py")
	opt = string.join(OPTS)
	for app in APPS:
		# build actual command to execute for this application
		sc = cmd + " " + opt + " -i " + app['icon'] + " " + app['script']
		subprocess.call(sc, shell=True)


# Copy additional resources
def copy_resources():
	print("Including resources...")
	for r in RES:
		print("Copying resource %s" % (r,))
		shutil.copy(r, os.path.join(get_build_path(), r))

##
## Main loop
##
if __name__ == '__main__':
	create_executables()
	copy_resources()
