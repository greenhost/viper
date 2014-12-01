#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Greenhost VOF
# https://greenhost.nl -\- https://greenhost.io
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os, subprocess, sys
from viper import tools

MS_SDK_DIR="%WINDIR%\Microsoft.NET\Framework\v3.5"


def build_clean_all():
	"""
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Cleaning build byproducts... 
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
	folders = [
		"dist/client",
		"dist/service",
		"dist/utils",
		"dist/doc",
		"build"
	]
	for f in folders:
		subprocess.call("rmdir {0} /s /q".format(f), shell=True)


def build_firewall_ctl():
	"""
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Building the firewall controller... 
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
	subprocess.call("{0}\msbuild.exe  firewall\fwipv6\fwipv6.sln /p:Configuration=Release /l:FileLogger,Microsoft.Build.Engine;logfile=Manual_MSBuild_ReleaseVersion_LOG.log".format(MS_SDK_DIR), shell=True)
	subprocess.call("xcopy firewall\fwipv6\bin\Release\*.* dist\utils /s /e /i /y")
	subprocess.call("xcopy firewall\fwipv6\bin\Release\*.exe utils /s /e /i /y")

def build_service():
	"""
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Building the Viper service...
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
	subprocess.call("python setup.py py2exe")

def build_client():
	"""
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Building the Viper client...
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
	subprocess.call("python buildexe.py")


def build_documentation():
	"""
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Copying documentation...
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	"""
	subprocess.call("xcopy doc dist\doc /s /e /i")

# def build_installer():
# 	"""
# 	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 	Compiling windows installer...
# 	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 	"""
# 	pass
# set FOUND=
# for %%i in (makensis.exe) do (set FOUND=%%~PATH:i)
# IF NOT DEFINED FOUND  (
# 	echo "!!! NSIS doesn't seem to be installed in your system. I cannot build the Windows installer without it."
# ) else (
# 	makensis scripts\viper-installer.nsi
# )

# :compress
# echo.
# echo.
# echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# echo Compressing installer file...
# echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @rename dist\viper-setup.exe viper-setup-%BUILD%.exe
# @7z a dist\viper-setup-%BUILD%.zip dist\viper-setup-%BUILD%.exe
 
# :sign_binaries
# echo.
# echo.
# echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# echo Signing build for release...
# echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# gpg --default-key viper@greenhost.nl --output dist\viper-setup-%BUILD%.zip.sig --detach-sig dist\viper-setup-%BUILD%.zip


# :end
def target_all():
	""" Build all targets """
	step_clean_all()
	step_firewall_ctl()
	step_service()
	step_client()

def target_clean():
	""" Clean up build byproducts """
	step_clean_all()

if __name__ == "__main__":
	from inspect import getmembers, isfunction
	targets = [o for o in getmembers(sys.modules[__name__]) if isfunction(o[1]) and ('target_' in o[0])]
	for t, f in targets:
		print("{0}\t\t-\t{1}".format(t, f.__doc__))
