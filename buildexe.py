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

PYINST_DEFAULT_PATH = 'C:\Python27\Lib\site-packages\PyInstaller'

# Apps to build, specifying the entry point script and the icon to
# embed in the executable file as a resource
APPS = [
		{'script': 'viperclient.py', 'icon': 'resources/icons/online.ico'}
	   ]

# PyInstaller options
OPTS = ['--onefile', '--noconsole']

# Additional application resources
RES  = ['__config.ovpn', 'README', 'resources', 'third-party/tap-windows', 'third-party/openvpn', 'dist/viperclient.exe']

# Build byproducts to delete after build
CLEAN = ['dist/viperclient.exe']

# relative to the CWD
def get_build_path():
	p = os.path.join(os.getcwd(), "dist\client")
	if not os.path.exists(p):
		os.makedirs(p)

	return p

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
		print(sc)
		subprocess.call(sc, shell=True)


# Copy additional resources
def copy_resources():
	print("Including resources...")
	for r in RES:
		print("Copying resource %s" % (r,))
		if not os.path.exists(r):
			print("WARNING: The requested resource %s could not be copied because source doesn't exist." % (r,))
			continue
		if os.path.isdir(r):
			print("\t-> as directory tree")
			shutil.copytree(r, os.path.join(get_build_path(), os.path.basename(r)) )
		else:
			print("\t-> as file")
			shutil.copy(r, os.path.join(get_build_path(), os.path.basename(r)) )

# Build windows services (PyInstaller doesn't seem to support services)
def py2exe_build_services():
	print("Building the windows service...")
	subprocess.call("python setup.py py2exe", shell=True)
	print("Sometimes when executing the py2exe command from a python script certain DLLs are not copied.\n\nRun this command to make sure they are copied: python setup.py py2exe")

def cleanup():
	for r in CLEAN:
		print("Cleaning byproduct %s" % (r,))
		os.remove(r)

##
## Main loop
##
if __name__ == '__main__':
	create_executables()
	copy_resources()
	cleanup()
	#py2exe_build_services()

