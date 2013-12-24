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
import os, sys, re
import json
import logging

provider = None

class ProviderSettings:
	def __init__(self):
		self.settings = {}

	def load(self, fn):
		logging.debug("Loading provider settings from '{0}'".format(fn))
		with open(fn) as f:
			self.settings = json.loads( f.read() )
			f.close()

	def get(self, name):
		return self.settings[name] if name in self.settings else None


def get_provider_setting(name):
	""" Get a configuration value from the provider file for the given key """
	global provider
	return provider.get(name)

provider = ProviderSettings()
provider.load('resources/provider.json')
