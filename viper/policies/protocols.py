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
import logging
from os import popen
from re import match
from pprint import pprint
from viper.tools import *
import subprocess

import viper.routing import *

@policy_export
class IPv6Policy(Policy):
	__command__ = "ipv6-off"
	def before_shield_up(self):
		self.verify()

	def after_shield_up(self):
		pass

	def before_shield_down(self):
		pass

	def after_shield_down(self):
		pass

	def verifyupdate(self):
		pass

	def verify(self):
	    logging.info("Checking fw entries for IPv6")

