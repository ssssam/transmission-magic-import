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

__metaclass__ = type
__all__ = [
    'Command',
    'register_command',
    'run'
]

import sys

import transmissionmagicimport.errors as errors


class Command:
    """Base class for Command objects"""

    doc = ''
    name = None

    def execute(self, config, help=None):
        return self.run(config, help=help)

    def run(self, config):
        """The body of the command"""
        raise NotImplementedError

# handle registration of new commands
_commands = {}


def register_command(command_class):
    _commands[command_class.name] = command_class

# special help command, never run


class cmd_help(Command):
    doc = 'Information about available commands'
    name = 'help'

    def run(self, config, help=None):
        if help:
            return help()

register_command(cmd_help)


def get_commands():
    return _commands


def run(command, config, help=None):
    # if the command hasn't been registered, load a module by the same name
    if command not in _commands:
        try:
            __import__('transmissionmagicimport.commands.%s' % command)
        except ImportError as e:
            if e.message.endswith(command):
                pass
            else:
                raise
    if command not in _commands:
        raise errors.FatalError('command not found')

    command_class = _commands[command]

    cmd = command_class()
    return cmd.execute(config, help=help)
