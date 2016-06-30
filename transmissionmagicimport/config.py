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

import os
import traceback
import types

import transmissionmagicimport.errors as errors

__all__ = ['Config']

_keys = ['input_path', 'search_paths',
         'exclude_trackers', 'avoid_data_paths',
         'transmission_hostname', 'transmission_port']


class Config:

    def __init__(self, filename='./config.rc'):
        self._config = {
            '__file__': filename  # _defaults_file
        }

        self.filename = filename

        if not os.path.exists(filename):
            raise errors.FatalError(
                'could not load config file, %s is missing' % filename)

        self.load()

    def load(self):
        config = self._config
        try:
            execfile(self.filename, config)
        except Exception, e:
            if isinstance(e, errors.FatalError):
                raise e
            traceback.print_exc()
            raise errors.FatalError('could not load config file')

        unknown_keys = []
        for k in config.keys():
            if k in _keys:
                continue
            if k[0] == '_':
                continue
            if type(config[k]) in (types.ModuleType, types.FunctionType, types.MethodType):
                continue
            unknown_keys.append(k)
        if unknown_keys:
            print('Unknown keys defined in configuration file: %s\n' %
                  ', '.join(unknown_keys))

        if 'input_path' not in config.keys() or 'search_paths' not in config.keys():
            raise errors.FatalError("config.rc does not have input_path or search_paths set, "
                                    "please edit the file.")

        # copy known config keys to attributes on the instance
        for name in _keys:
            setattr(self, name, config.get(name, []))
