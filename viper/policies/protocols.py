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

from viper import policies

from viper.routing import *
from viper.windows import firewall

@policies.policy_export
class IPv6Policy(policies.Policy):
	__command__ = "ipv6-off"
	def before_open_tunnel(self):
		logging.debug("IPv6Policy.before_open_tunnel() called")
		return firewall.block_ipv6()

	def after_open_tunnel(self):
		pass

	def before_close_tunnel(self):
		pass

	def after_close_tunnel(self):
		logging.debug("IPv6Policy.after_close_tunnel() called")
		return firewall.unblock_ipv6()

	def verify(self):
		pass

