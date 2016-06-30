#
# Copyright (C) 2011 Sam Thursfield
#
# This file is part of Transmission Magic Import.
#
# Transmission Magic Import is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Transmission Magic Import is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Transmission Magic Import.  If not, see <http://www.gnu.org/licenses/>.
#


class TMIException(Exception):
    pass


class ConfigError(TMIException):
    '''A problem in a configuration file.'''


class FatalError(TMIException):
    '''Now we quit.'''
