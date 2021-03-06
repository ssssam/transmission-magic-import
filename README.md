# Transmission Magic Import

Transmission Magic Import is a program to organise a heap of torrents which
have been separated from their data. It's useful if for example you need to
import all your .torrent files into Transmission from different software,
or if want to migrate from one user's Transmission instance to another.

It has not been well-tested, but it is released is in the hope that it is
useful to someone else.

Transmission keeps its downloaded torrent files by default in
~/.config/transmission/torrents.

Instructions:

  1. create config.rc (see config.rc.example)
  2. `./transmission-magic-import info`: reads available torrent files
     and displays information, which may be helpful in completing
     config.rc
  3. `./transmission-magic-import search`: locate torrent data and save
     to ./transmission-magic-import.results
  4. `./transmission-magic-import import`: add found torrents to a
     running Transmission instance, using RPC

Other commands:

* `clean-torrents`: remove duplicate .torrent files and torrents with trackers
  listed in exclude_trackers.
* `clean-data`: list duplicate downloads of torrent data. You can feed this into
  rm -R if you like. This command connects to a running Transmission instance,
  and will change the torrents' data location if it is in one of the
  avoid_data_paths and also exists elsewhere.

To move the duplicate data to a single directory (I wouldn't trust the script
enough to just delete it :), use the following in the shell:

./transmission-magic-import.py clean-data | while read line; do mv "$line" ~/torrent-duplicates; done

Hope this is useful!

Sam Thursfield <ssssam@gmail.com>, 13th Feb 2011 
