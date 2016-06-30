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

import transmissionrpc

import glob
import os

import transmissionmagicimport.commands
import transmissionmagicimport.errors
from transmissionmagicimport.torrentindex import TorrentIndex, load_index
import transmissionmagicimport.utils


class cmd_clean_data (commands.Command):
    name = 'clean-data'

    def run(self, config, help=None):
        index = load_index()

        try:
            tc = transmissionrpc.Client(
                config.transmission_hostname, port=config.transmission_port)
        except transmissionrpc.transmission.TransmissionError as e:
            raise errors.FatalError("Unable to connect to a Transmission at %s:%i. %s.\n\n"
                                    "Make sure Transmission is running, the web client is "
                                    "enabled in the preferences and its details match the "
                                    "settings in config.rc. Make sure transmission-daemon is "
                                    "not running if you are trying to connect to a GUI instance."
                                    % (config.transmission_hostname, config.transmission_port, e))

        tc_list = tc.list()

        for torrent in index.torrents:
            if len(torrent.data_matches) < 2:
                continue

            data_path = torrent.choose_data_path()
            if data_path == None:
                continue

            tc_torrent = utils.transmission_find_torrent(tc_list, torrent)

            if tc_torrent:
                tc.locate(tc_torrent.hashString, data_path)

            for spare_data in torrent.data_matches[1:]:
                path = os.path.join(
                    spare_data[0], utils.normalise_path(torrent.name))
                #path =  path.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")
                print("%s" % path)

                # Here's the version of the data that's actually being used
                # os.path.join (torrent.data_matches[0][0],
                # utils.normalise_path (torrent.name)))


commands.register_command(cmd_clean_data)
