#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name="playist",
    version="0.1",
    packages=["playist"],
    # http://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation  # noqa
    entry_points={
        'console_scripts': [
            'playist = playist.playist:main',
        ],
    },

    author="Von Welch",
    author_email="von@vwelch.com",
    description="Manage mp3 playlists",
    license="Apache2",
)
