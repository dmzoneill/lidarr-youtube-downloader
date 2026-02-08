# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["lidarr_youtube_downloader"]

package_data = {"": ["*", "view/*", "lidarr_youtube_downloader/view/*"]}

install_requires = ["requests", "youtube-search-python", "eyed3", "typer", "yt-dlp"]

entry_points = {
    "console_scripts": [
        "lyd = lidarr_youtube_downloader.lyd:app",
        "lyd-unmapped = lidarr_youtube_downloader.lyd-unmapped:app",
    ]
}

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup_kwargs = {
    "name": "lidarr-youtube-downloader",
    "version": "0.3.33",
    "description": "",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "David O Neill",
    "author_email": "dmz.oneill@gmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": "https://github.com/dmzoneill/lidarr-youtube-downloader",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "include_package_data": True,
    "python_requires": ">=3.10,<4.0",
}


setup(**setup_kwargs)
