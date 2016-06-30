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

import bcoding

import glob
import os
import pickle
import sys
import urllib.parse
import warnings

import transmissionmagicimport.config as config
import transmissionmagicimport.errors as errors
import transmissionmagicimport.utils as utils


def torrent_info_matches(info_1, info_2):
    """Returns True if two torrents reflect the same data."""
    # I guess if you have two torrents on the exact same data with different
    # trackers, you lose.
    if 'files' in info_1:
        if 'files' not in info_2:
            return False
        if info_1['files'] != info_2['files']:
            return False
    if info_1['pieces'] != info_2['pieces']:
        return False
    return True


def load_index():
    """Load pickled search results"""

    try:
        results_file = open('transmission-magic-import.results', 'rb')
        index = pickle.load(results_file)
        results_file.close()
        print("Read ./transmission-magic-import.results")
    except EOFError:
        raise errors.FatalError("Unable to read file transmission-magic-import.results.\n\n"
                                "Please run 'transmission-magic-import search'.")
    except IOError:
        raise errors.FatalError("Unable to find file transmission-magic-import.results.\n\n"
                                "Please run 'transmission-magic-import search'.")
    return index


class Torrent:

    def __init__(self, filename, name, type, file_info):
        self.filename = filename
        self.name = name
        self.type = type
        self.file_info = file_info

        # Paths where data was found, in pair form (path, match_strength)
        self.data_matches = []

    def __repr__(self):
        return "torrent: %s" % self.filename

    def check_data_file(self, path, length):
        """Calculate match strength of the data for the torrent. This is based on if each file
           exists (1 point) and if the file size matches (0-1 points based on relative size
           difference)"""
        if not os.path.isfile(path):
            path = utils.normalise_path(path)
            if not os.path.isfile(path):
                return 0.0

        if length == 0:
            print("Warning: %s has length 0" % path)
            return 2.0

        data_file_size = os.stat(path).st_size
        size_match = 1.0 - (float(abs(data_file_size - length)
                                  ) / float(max(data_file_size, length)))
        return size_match + 1.0

    @staticmethod
    def expand_data_file_path(host_path, data_file_path):
        """Expand the path to one file of a torrent's payload."""
        # It's not entirely clear whether the torrent format encodes
        # paths in a specific way. We seem to receive both strings and
        # bytes types, for different ones, so let's handle both cases
        # and avoid making any assumptions about the encoding of the
        # path within the torrent file.
        #
        # In the case that we receive an encoded path from the torrent,
        # we assume the host filesystem encodes paths as UTF-8 in order
        # to encode the host path. This is hopefully true but not guaranteed.
        if isinstance(data_file_path[0], bytes):
            result = os.path.join(
                host_path.encode('utf-8'),
                b'/'.join(data_file_path))
        else:
            result = os.path.join(
                host_path,
                '/'.join(data_file_path))
        return result

    def add_data_path(self, config, path):
        # Calculate how much the data matches the torrent (looking at names and sizes only, we
        # don't read the actual data)
        #
        if self.type == 'single':
            assert (os.path.isfile(path))
            match_strength = self.check_data_file(
                path, self.file_info['length']) / 2.0
        else:
            assert (os.path.isdir(path))
            match_strength = 0.0
            for data_file_info in self.file_info['files']:
                data_file_path = self.expand_data_file_path(
                        path, data_file_info['path'])
                match_strength += self.check_data_file(
                    data_file_path, data_file_info['length'])
            match_strength /= (2.0 * len(self.file_info['files']))

        for avoid_path in config.avoid_data_paths:
            if path.startswith(avoid_path):
                match_strength = max(match_strength - 0.1, 0.0)

        # Store the match; remember 'path' is the actual data, so the torrent's data location is
        # actually its parent.
        self.data_matches.append((os.path.split(path)[0], match_strength))
        return match_strength

    def choose_data_path(self):
        """Returns the location found which seems most likely to hold this torrent's data"""
        if len(self.data_matches) == 0:
            return None
        self.data_matches.sort(key=lambda m: m[1], reverse=True)
        return self.data_matches[0][0]


class TorrentIndex:

    def __init__(self, config, store_ignored=False):
        self.config = config
        self.store_ignored = store_ignored
        self.excluded = 0
        self.duplicates = 0

        # List of torrent objects
        self.torrents = []

        # Mappings from a torrent name (which will normally match the directory to which the files
        # were downloaded) to a list of .torrent filenames that have that name, separated into
        # single-file and multi-file torrents.
        self.names_single = {}
        self.names_multi = {}

        # List of all trackers found in the input torrents
        self.trackers = []

        if store_ignored:
            # Unwanted torrents, stored for use by 'clean-torrents' command
            self.duplicate_torrent_files = []
            self.excluded_torrent_files = []

        print("Reading torrent files ...")

        # Iterate through every .torrent file below 'config.input_path'
        for dirpath, dirnames, filenames in os.walk(config.input_path):
            for f in filenames:
                if f.endswith('.torrent'):
                    self.read_torrent(os.path.join(dirpath, f))

        print(".. done, found %i torrents" % len(self.torrents), end=' ')

        if len(self.torrents) == 0:
            sys.stderr.write("transmission-magic-import: no files found in path '%s'\n"
                             % config.input_path)
            sys.exit(1)

        if self.duplicates:
            print("with %i duplicates" % self.duplicates, end=' ')
        if self.excluded:
            print("and %i excluded by tracker" % self.excluded, end=' ')
        print("\n")

        # Free piece data, we don't need it now the duplicates are gone, and it
        # takes up a fair amount of memory
        for torrent in self.torrents:
            torrent.file_info['pieces'] = None

    def read_torrent(self, filename):
        torrent_file = open(filename, 'rb')

        torrent_data = bcoding.bdecode(torrent_file.read())

        if 'announce' not in torrent_data:
            warnings.warn("No 'announce' URL found in %s; ignoring" % filename)
            return

        # Get tracker hostname, see if this torrent should be ignored
        #
        tracker_url = urllib.parse.urlparse(torrent_data['announce'])
        tracker_hostname = tracker_url.hostname

        # Store tracker even if it's excluded; this list is only used for
        # 'info'
        if tracker_hostname not in self.trackers:
            self.trackers.append(tracker_hostname)

        if tracker_hostname in self.config.exclude_trackers:
            if store_ignored:
                self.excluded_torrent_files.append(filename)
            self.excluded += 1
            torrent_file.close()
            return

        type = 'single'
        if 'files' in torrent_data['info']:
            type = 'multi'

        name = torrent_data['info']['name']
        name_index = getattr(self, "names_" + type)

        # Check for duplicates
        is_duplicate = False
        if name in name_index:
            for existing_torrent in name_index[name]:
                if torrent_info_matches(existing_torrent.file_info, torrent_data['info']):
                    is_duplicate = True
                    self.duplicates += 1
                    break
        if is_duplicate:
            if self.store_ignored:
                self.duplicate_torrent_files.append(filename)
            torrent_file.close()
            return

        torrent = Torrent(filename, name, type, torrent_data['info'])
        self.torrents.append(torrent)

        if name in name_index:
            name_index[name].append(torrent)
        else:
            name_index[name] = [torrent]

        torrent_file.close()

    def purge_stage1(self):
        """Remove data not needed for 'import' command to save space in .results file"""
        for t in self.torrents:
            t.file_info = None

    def save(self):
        results_file = open('transmission-magic-import.results', 'wb')
        pickle.dump(self.torrents, results_file)
        results_file.close()
        print("\nWrote ./transmission-magic-import.results\n")
