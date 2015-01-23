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
from viper.tools import *

from viper import policies
from viper.policies import protocols, routing


@policies.policy_export
class StrictPolicy(policies.Policy):
    __command__ = "strict"
    _builtins = [protocols.IPv6Policy(),
                routing.LocalSubnetPolicy(),
                routing.CrossCheckPolicy(),
                routing.MonitorGatewayMutation(),
                routing.MonitorSplitRoutes()]
    def before_open_tunnel(self):
        logging.debug("StrinctPolicy.before_open_tunnel() called")
        for pol in self._builtins:
            pol.before_open_tunnel()

    def after_open_tunnel(self):
        logging.debug("StrinctPolicy.after_open_tunnel() called")
        for pol in self._builtins:
            pol.after_open_tunnel()

    def before_close_tunnel(self):
        logging.debug("StrinctPolicy.before_close_tunnel() called")
        for pol in self._builtins:
            pol.before_close_tunnel()

    def after_close_tunnel(self):
        logging.debug("StrinctPolicy.after_close_tunnel() called")
        for pol in self._builtins:
            pol.after_close_tunnel()

    def verify(self):
        logging.debug("StrinctPolicy.verify() called")
        for pol in self._builtins:
            pol.verify()

@policies.policy_export
class LaxPolicy(policies.Policy):
    __command__ = "lax"
    _builtins = [protocols.IPv6Policy(),
                routing.MonitorGatewayMutation()
                ]
    def before_open_tunnel(self):
        logging.debug("LaxPolicy.before_open_tunnel() called")
        for pol in self._builtins:
            pol.before_open_tunnel()

    def after_open_tunnel(self):
        logging.debug("LaxPolicy.after_open_tunnel() called")
        for pol in self._builtins:
            pol.after_open_tunnel()

    def before_close_tunnel(self):
        logging.debug("LaxPolicy.before_close_tunnel() called")
        for pol in self._builtins:
            pol.before_close_tunnel()

    def after_close_tunnel(self):
        logging.debug("LaxPolicy.after_close_tunnel() called")
        for pol in self._builtins:
            pol.after_close_tunnel()

    def verify(self):
        logging.debug("LaxPolicy.verify() called")
        for pol in self._builtins:
            pol.verify()
