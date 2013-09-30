#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
#
# @license
#
import os, sys
import fnmatch, glob

LICENSE = """GNU GENERAL PUBLIC LICENSE v3

Viper - Best-practice based VPN management software
Copyright (C) 2013 Greenhost VOF

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

def list_sources(root = '.', extensions = ['*.py', '*.cs', '*.bat']):
	matches = []
	for root, dirnames, filenames in os.walk(root):
		for ext in extensions:
			for filename in fnmatch.filter(filenames, ext):
				fn = os.path.join(root, filename)
				matches.append(fn)
				print fn

	return matches

def interp_license(fn):
	with open(fn+".out", 'w') as fout:
		with open(fn, 'r') as fin:
		    for line in fin:
		        if '@license' in line:
		        	prefix = line[0:line.find("@license")]
		        	# @todo insert license
		        	for l in LICENSE.splitlines():
		        		fout.write( "{0}{1}\n".format(prefix, l) )
		        else:
		        	fout.write(line)


def main():
	lst = list_sources('.')
	for fn in lst:
		interp_license(fn)

if __name__ == '__main__':
	main()