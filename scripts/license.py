#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
#
# @license
#
import os, sys
import fnmatch, glob
import shutil

LICENSE = """Copyright (c) 2013 Greenhost VOF and contributors

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.
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
	fnout = fn+".out"
	with open(fnout, 'w') as fout:
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
		shutil.copy(fn+".out", fn)
		os.unlink(fn+".out")

if __name__ == '__main__':
	main()
