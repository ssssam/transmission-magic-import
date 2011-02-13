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

import os;
import sys;

import commands;
import errors;
from config import Config;

help = \
"""\ntransmission-magic-import: Organiser for stray .torrent files

Instructions:
  1. create config.rc (see config.rc.example)
  2. ./transmission-magic-import info: reads available torrent files
     and displays information, which may be helpful in completing
     config.rc
  3. ./transmission-magic-import search: locate torrent data and save
     to ./transmission-magic-import.results
  4. ./transmission-magic-import import: add found torrents to a
     running Transmission instance, using RPC

Other commands:
  clean-torrents: remove duplicate .torrent files and torrents with trackers
                  listed in exclude_trackers.
      clean-data: list duplicate downloads of torrent data. You can feed this
                  into rm -R if you like. This command connects to a running
                  Transmission instance, and will change the torrents' data
                  location if it is in one of the avoid_data_paths and also
                  exists elsewhere.
"""

def print_help():
	print help

def main(args):
	if not args:
		print_help ()
		sys.exit(1)

	command = args[0]

	try:
		config = Config()
	except errors.FatalError, exc:
		sys.stderr.write("transmission-magic-import: %s\n" % exc.args[0])
		sys.exit(1)

	try:
		rc = commands.run (command, config, help = print_help)
	except errors.FatalError, exc:
		sys.stderr.write('\ntransmission-magic-import %s: %s\n' % (command, exc))
		sys.exit(1)
	except KeyboardInterrupt:
		uprint('Interrupted')
		sys.exit(1)

	if rc:
		sys.exit(rc)
