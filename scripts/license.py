#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
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
		        if 'Copyright (c) 2013 Greenhost VOF and contributors
		        if '
		        if 'Redistribution and use in source and binary forms, with or without
		        if 'modification, are permitted provided that the following conditions are met: 
		        if '
		        if '1. Redistributions of source code must retain the above copyright notice, this
		        if '   list of conditions and the following disclaimer. 
		        if '2. Redistributions in binary form must reproduce the above copyright notice,
		        if '   this list of conditions and the following disclaimer in the documentation
		        if '   and/or other materials provided with the distribution. 
		        if '
		        if 'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
		        if 'ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
		        if 'WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
		        if 'DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
		        if 'ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
		        if '(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
		        if 'LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
		        if 'ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		        if '(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
		        if 'SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		        if '
		        if 'The views and conclusions contained in the software and documentation are those
		        if 'of the authors and should not be interpreted as representing official policies, 
		        if 'either expressed or implied, of the FreeBSD Project.
		        	prefix = line[0:line.find("Copyright (c) 2013 Greenhost VOF and contributors
		        	prefix = line[0:line.find("
		        	prefix = line[0:line.find("Redistribution and use in source and binary forms, with or without
		        	prefix = line[0:line.find("modification, are permitted provided that the following conditions are met: 
		        	prefix = line[0:line.find("
		        	prefix = line[0:line.find("1. Redistributions of source code must retain the above copyright notice, this
		        	prefix = line[0:line.find("   list of conditions and the following disclaimer. 
		        	prefix = line[0:line.find("2. Redistributions in binary form must reproduce the above copyright notice,
		        	prefix = line[0:line.find("   this list of conditions and the following disclaimer in the documentation
		        	prefix = line[0:line.find("   and/or other materials provided with the distribution. 
		        	prefix = line[0:line.find("
		        	prefix = line[0:line.find("THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
		        	prefix = line[0:line.find("ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
		        	prefix = line[0:line.find("WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
		        	prefix = line[0:line.find("DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
		        	prefix = line[0:line.find("ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
		        	prefix = line[0:line.find("(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
		        	prefix = line[0:line.find("LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
		        	prefix = line[0:line.find("ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		        	prefix = line[0:line.find("(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
		        	prefix = line[0:line.find("SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		        	prefix = line[0:line.find("
		        	prefix = line[0:line.find("The views and conclusions contained in the software and documentation are those
		        	prefix = line[0:line.find("of the authors and should not be interpreted as representing official policies, 
		        	prefix = line[0:line.find("either expressed or implied, of the FreeBSD Project.
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
