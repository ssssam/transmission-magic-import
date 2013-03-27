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

import transmissionrpc;

import glob;
import os;
import urllib;

import commands
import errors
from torrentindex import TorrentIndex, load_index;
import utils

class cmd_import (commands.Command):
	name = 'import'

	def run(self, config, help=None):
		torrents = load_index()

		try:
			tc = transmissionrpc.Client(config.transmission_hostname, port=config.transmission_port)
		except transmissionrpc.transmission.TransmissionError, e:
			raise errors.FatalError ("Unable to connect to a Transmission at %s:%i. %s.\n\n"
			                         "Make sure Transmission is running, the web client is "
			                         "enabled in the preferences and its details match the "
			                         "settings in config.rc. Make sure transmission-daemon is "
			                         "not running if you are trying to connect to a GUI instance."
			                         % (config.transmission_hostname, config.transmission_port, e))

		tc_existing_torrents = tc.list()

		newly_queued = 0
		already_present = 0

		for torrent in torrents:
			data_path = torrent.choose_data_path()
			if data_path == None: continue

			if utils.transmission_find_torrent (tc_existing_torrents, torrent) != None:
				already_present += 1
				continue

			uri = 'file://' + urllib.pathname2url(torrent.filename)
			try:
				tc_list = tc.add_uri (uri, download_dir=data_path,
				                      paused=True)
			except transmissionrpc.error.TransmissionError as e:
				raise transmissionrpc.error.TransmissionError(
			for key, value in tc_list.iteritems():
				tc_torrent_id = key
				tc_torrent = value
			tc.verify (tc_torrent_id)

			tc_existing_torrents.update(tc_list)

			newly_queued += 1

		print "\nAdded to queue: %i (already present: %i)" % (newly_queued, already_present)

commands.register_command (cmd_import)
