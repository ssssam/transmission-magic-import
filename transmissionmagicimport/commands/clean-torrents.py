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

import transmissionmagicimport.commands as commands
from transmissionmagicimport.torrentindex import TorrentIndex


class cmd_clean_torrents(commands.Command):
    name = 'clean-torrents'

    def run(self, config, help=None):
        index = TorrentIndex(config, store_ignored=True)

        if len(index.duplicate_torrent_files) > 0:
            for file in index.duplicate_torrent_files:
                os.remove(file)
            print("\nclean-torrents: Removed %i duplicate .torrent files" % \
                  len(index.duplicate_torrent_files))

        if len(index.excluded_torrent_files) > 0:
            for file in index.excluded_torrent_files:
                os.remove(file)
            print("\nclean-torrents: Removed %i excluded torrents" % \
                  len(index.excluded_torrent_files))

        if len(index.duplicate_torrent_files) == 0 and len(index.excluded_torrent_files) == 0:
            print("\nclean-torrents: Nothing to remove.")
commands.register_command(cmd_clean_torrents)
