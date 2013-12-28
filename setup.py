#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name="playlist",
    version="0.1",
    packages=["playlist"],
    # http://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation  # noqa
    entry_points={
        'console_scripts': [
            'playlist = playlist.playlist:main',
        ],
    },

    author="Von Welch",
    author_email="von@vwelch.com",
    description="Manage mp3 playlists",
    license="Apache2",
)
