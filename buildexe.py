import os, sys
import time, string
import subprocess
import shutil

PYINST_DEFAULT_PATH = 'C:\pyinstaller-2.0'

APPS = [
		{'script': 'winservice.py', 'icon' : 'monitor.ico'},
		{'script': 'umanager.py', 'icon': 'online.ico'}
	   ]
OPTS = ['--onefile', '--noconsole']
RES  = ['__config.ovpn', 'online.ico', 'offline.ico', 'README']

def get_build_path():
	return "./dist"

def get_pyinstaller_path():
	p = os.getenv("PYINSTALLER_HOME")
	if p:
		return p
	else:
		return PYINST_DEFAULT_PATH

def create_executables():
	print("Creating executables...")
	path = get_pyinstaller_path()
	cmd = os.path.join(path, "pyinstaller.py")
	opt = string.join(OPTS)
	for app in APPS:
		sc = cmd + " " + opt + " -i " + app['icon'] + " " + app['script']
		subprocess.call(sc, shell=True)


def copy_resources():
	print("Including resources...")
	for r in RES:
		print("Copying resource %s" % (r,))
		shutil.copy(r, os.path.join(get_build_path(), r))

if __name__ == '__main__':
	create_executables()
	copy_resources()
