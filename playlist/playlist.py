#!/usr/bin/env python
"""An example of subcommands with argparse """
from __future__ import print_function  # So we can get at print()

import argparse
import glob
import os.path
import shutil
import string
import sys

# Output functions
output = print


class Playlist(object):
    _files = []
    _base_path = "."

    def __init__(self, files=None, base_path="."):
        """Create playlist containing files, if given"""
        if files:
            self._files.extend(files)
        self._base_path = base_path

    def add(self, filename):
        """Add gilename to playlist"""
        self._files.append(os.path.relpath(filename, self._base_path))

    def copy_to(self, path):
        """Copy playlist files to given path"""
        for f in self.file_paths():
            d = os.path.join(path, os.path.relpath(f, self._base_path))
            if not os.path.exists(os.path.dirname(d)):
                os.makedirs(os.path.dirname(d))
            shutil.copy(f, d)

    def files(self):
        """Return files with paths relative to base"""
        return self._files

    def file_paths(self):
        """Return path to full paths to files"""
        return [os.path.abspath(os.path.join(self._base_path, filename))
                for filename in self._files]

    def find_missing(self):
        """Return list containing non-existant files in playlist"""
        missing = [file for file in self.file_paths()
                   if not os.path.exists(file)]
        return missing

    def full_path(self, filename):
        """Given a filename from the playlist, return its full path"""
        return os.path.join(self._base_path, filename)

    def read_file(self, path):
        """Read file and add to playlist"""
        with open(path) as f:
            files = [string.rstrip(fn) for fn in f.readlines()]
        # Filter comments
        files = [file for file in files if not file.startswith("#")]
        self._files.extend(files)

    def save_to_file(self, path):
        """Save playlist to given file"""
        with open(path, "w") as f:
            for file in self._files:
                f.write(file + "\n")

    def size(self):
        """Return size of playlist in bytes"""
        size = sum([os.path.getsize(f) for f in self.file_paths()])
        return size

    def __len__(self):
        return len(self._files)


######################################################################
#
# Sub-commands


def add(args):
    """Add given filename patterns to playlist"""
    playlist = load_playlist(args)
    count = 0
    for pattern in args.patterns:
        if os.path.isdir(pattern):
            # Load all mp3s under given directory
            for (dirpath, dirnames, filenames) in os.walk(pattern):
                mp3s = [f for f in filenames if f.endswith(".mp3")]
                for file in mp3s:
                    playlist.add(os.path.join(dirpath, file))
                    count += 1
        else:
            # Treat as glob
            for filename in glob.glob(pattern):
                playlist.add(filename)
                count += 1
    output("{} files added to {} ({} total)".format(count,
                                                    args.playlist,
                                                    len(playlist)))
    if count:
        playlist.save_to_file(args.playlist)


def check(args):
    """Check playlist for missing files

    Returns 1 if any are missing, 0 otherwise"""
    playlist = load_playlist(args)
    missing = playlist.find_missing()
    if missing:
        output("{} file{} missing.".format(len(missing),
                                           "s" if len(missing) > 1 else ""))
        map(output, missing)
    return 1 if missing else 0


def size(args):
    """Print size of playlist"""
    playlist = load_playlist(args)
    size = playlist.size()
    # Kudos: http://stackoverflow.com/a/1094933/197789
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
        # Will fall through if >PB and display in TBs
    output("%3.1f %s" % (size, unit))
    return 0


def sync(args):
    """Sync playlist with device

    Deletes any files on device not in playlist."""
    playlist = load_playlist(args)

    # Get list of files in target path
    dest_files = []
    for (dirpath, dirnames, filenames) in os.walk(args.device_path):
        dest_files.extend(
            [os.path.relpath(os.path.join(dirpath, f), args.device_path)
             for f in filenames])

    dest_missing = [f for f in playlist.files() if f not in dest_files]
    output("Copying {} file{} to {}".format(
        len(dest_missing),
        "s" if len(dest_missing) != 1 else "",
        args.device_path))
    for f in dest_missing:
        d = os.path.join(args.device_path, f)
        if not os.path.exists(os.path.dirname(d)):
            os.makedirs(os.path.dirname(d))
        shutil.copy(playlist.full_path(f), d)

    playlist_missing = [f for f in dest_files if f not in playlist.files()]
    output("Removing {} file{} from {}".format(
        len(playlist_missing),
        "s" if len(playlist_missing) != 1 else "",
        args.device_path))
    for f in playlist_missing:
        d = os.path.join(args.device_path, f)
        os.remove(d)

    # Remove any empty directories in destination
    for (dirpath, dirnames, filenames) in os.walk(args.device_path,
                                                  topdown=False):
        if len(dirnames) == 0 and len(filenames) == 0:
            os.rmdir(dirpath)


######################################################################
#
# Helper functons


def create_playlist(args):
    """Create Playlist object given arguments"""
    playlist = Playlist(base_path=args.base_path)
    return playlist


def load_playlist(args):
    """Load playlist from file and return"""
    playlist = create_playlist(args)
    if os.path.exists(args.playlist):
        playlist.read_file(args.playlist)
    return playlist

######################################################################


def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Argument parsing
    parser = argparse.ArgumentParser(
        description=__doc__,  # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # To have --help print defaults with trade-off it changes
        # formatting, use: ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-b', '--base_path', default='.',
                        help='path to music', metavar='path')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_add = subparsers.add_parser('add', help=add.__doc__)
    parser_add.set_defaults(func=add)
    parser_add.add_argument('playlist',
                            help='path to playlist', metavar='path')
    parser_add.add_argument('patterns', nargs='+',
                            help='pattern to add', metavar='pattern')

    parser_check = subparsers.add_parser('check', help=check.__doc__)
    parser_check.set_defaults(func=check)
    parser_check.add_argument('playlist',
                              help='path to playlist', metavar='path')

    parser_size = subparsers.add_parser('size', help=size.__doc__)
    parser_size.set_defaults(func=size)
    parser_size.add_argument('playlist',
                             help='path to playlist', metavar='path')

    parser_sync = subparsers.add_parser('sync', help=sync.__doc__)
    parser_sync.set_defaults(func=sync)
    parser_sync.add_argument('playlist',
                             help='path to playlist', metavar='path')
    parser_sync.add_argument('device_path',
                             help='path to device', metavar='path')

    args = parser.parse_args()
    func = args.func
    status = func(args)
    return status

if __name__ == "__main__":
    sys.exit(main())
