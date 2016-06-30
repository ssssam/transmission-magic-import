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
import transmissionmagicimport.config as config
from transmissionmagicimport.torrentindex import TorrentIndex


class Search:

    def __init__(self, config, index):
        self.config = config
        self.index = index
        #self.unmatched_torrents = index.torrents

    def match_on_name(self, data_path, torrent_list):
        for torrent in torrent_list:
            # Associate path with torrent, if the contents match
            torrent.add_data_path(self.config, data_path)

    def search_directory_fast(self, path):
        """Search for torrent data by matching directory or file names with the torrent name."""
        if not os.access(path, os.R_OK):
            if os.path.split(path)[1] != 'lost+found':
                print("Warning: cannot read %s" % path)
            return

        if path[len(path) - 1] == '/':
            path = path[0:-1]

        # Match directory name with a multi-file torrent's name; this is the fast route
        #
        dir_name = os.path.split(path)[1]
        if dir_name in self.index.names_multi:
            self.match_on_name(path, self.index.names_multi[dir_name])

        # Search subdirs now, so we can hopefully match as many torrents as
        # possible the quick way
        contents = os.listdir(path)

        # If we matched and there are no more files outside the torrent, there can't be any
        # more torrent data in this directory
        # if (match == 1.0 and len(contents) ==

        for subdir in contents:
            subdir_path = os.path.join(path, subdir)
            if os.path.isdir(subdir_path):
                self.search_directory_fast(subdir_path)

        # See if the files here match any single-file torrent names.
        for filename in contents:
            if filename in self.index.names_single:
                self.match_on_name(os.path.join(path, filename),
                                   self.index.names_single[filename])


class cmd_search(commands.Command):
    name = 'search'

    def run(self, config, help=None):
        index = TorrentIndex(config)

        search = Search(config, index)

        for path in config.search_paths:
            search.search_directory_fast(path)

        unmatched_list = []
        for torrent in index.torrents:
            if len(torrent.data_matches) == 0:
                unmatched_list.append(torrent)
            # elif len(torrent.data_matches) > 1:
            # print "More than one location for %s: %s" % (torrent,
            # torrent.data_matches)

        print("\nTorrents missing their data: ")
        for torrent in unmatched_list:
            print("\t%s" % os.path.basename(torrent.filename))

        index.purge_stage1()
        index.save()

commands.register_command(cmd_search)
