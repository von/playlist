playlist
========

A script for managing mp3 playlists.

[https://github.com/von/playlist](https://github.com/von/playlist)

Installation
------------

    git clone https://github.com/von/playlist.git
    cd playlist
    ./setup.py install

Usage
-----

Add files to a playlist:

    playlist add <playlist file> <pattern>

Where `pattern` is either a directory or a glob. If a directory, all
mp3s under that directory are found and added.

Check files in playlist to make sure they exist:

    playlist check <playlist file>

Calculate size of files in playlist:

    playlist size <playlist file>

Sync files in playlist to device:

    playlist sync <playlist file> <device path>

Options
-------

    -b <path>     Relative path of files in playlist.

