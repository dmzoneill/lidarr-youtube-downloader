# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["lidarr_youtube_downloader"]

package_data = {"": ["*", "view/*", "lidarr_youtube_downloader/view/*"]}

install_requires = ["requests", "youtube-search-python", "eyed3"]

entry_points = {
    "console_scripts": [
        "lyd = lidarr_youtube_downloader.lyd:app",
    ]
}

setup_kwargs = {
    "name": "lidarr-youtube-downloader",
    "version": "0.3.33",
    "description": "",
    "long_description": '# lidarr-youtube-downloader\n\nLook for missing tracks in your lidarr library and download them from youtube.\n\n# Docker Usage\n\n### docker run\n```\ndocker build -t lyd .\n# you need to be careful that the path matches the path that lidarr knows\ndocker run \\n   -v /path/to/music:/path/to/music \\n   -v /path/to/db/file:/path/to/db/file \   \n   -e LIDARR_URL="http://HOST_IP:8686" \\n   -e LIDARR_API_KEY="771de60596e946f6b3e5e6f5fb6fd729" \\n   -e LIDARR_DB="/path/to/lidarr/lidarr.db" \\n   -e LIDARR_MUSIC_PATH="/music" \\n   --name lyd lyd\n```\n\n# Local Usage\n\n### Requirements\n```\ndnf/apt install ffmpeg\nsudo curl https://youtube-dl.org/downloads/latest/youtube-dl -o /usr/bin/youtube-dl\nchmod +x /usr/bin/youtube-dl\npip3 install eyed3 youtube-search-python\n```\n\n### Config\n```\nexport LIDARR_URL="http://127.0.0.3:8686"\nexport LIDARR_API_KEY="771de60596e946f6b3e5e6f5fb6fd729" # your key\nexport LIDARR_DB="/path/to/lidarr/lidarr.db"\nexport LIDARR_MUSIC_PATH="/music"\n```\n\n### Usage\n```\npip3 install lidarr-youtube-downloader\nlyd\n```\n\n# Sample output\n```\nAlbum: 34/545   Track: 71/226\n================================================================================\n\n    Path           : /music/The Beatles\n    Artist         : The Beatles\n    Album          : The Beatles\n    Track          : Norwegian Wood (This Bird Has Flown)\n    Genre          : Acoustic Rock\n    Date           : 1988\n    CD Count       : 16\n    CD No          : 6\n    Track No       : 2/12\n\n    Youtube search\n    ========================================\n        \n        Best title: The Beatles - Norwegian Wood (This Bird Has Flown)\n        Best match: 1.0\n        \n        Selected https://www.youtube.com/watch?v=W15_1kE08Gc\n\n    Youtube-dl\n    ========================================\n\n        youtube-dl\n            --no-progress\n            -x\n            --audio-format mp3 "https://www.youtube.com/watch?v=W15_1kE08Gc"\n            -o \n            "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"\n\n\n        Downloaded successfully\n\n        [youtube] W15_1kE08Gc: Downloading webpage\n        [youtube] W15_1kE08Gc: Downloading MPD manifest\n        [download] Destination: /music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3\n        [download] Download completed\n        [ffmpeg] Correcting container in "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"\n        [ffmpeg] Post-process file /music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3 exists, skipping\n\n    Ffmpeg\n    ========================================\n\n        ffmpeg -i "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"\n            -metadata artist="The Beatles"\n            -metadata year="1988"\n            -metadata title="Norwegian Wood (This Bird Has Flown)"\n            -metadata album="The Beatles"\n            -metadata track="2"\n            -metadata genre="Acoustic Rock"\n            -hide_banner\n            -loglevel error\n            "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"\n\n        ffmpeg added mp3 tag      \n\n```\n',
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
    "python_requires": ">=3.8,<4.0",
}


setup(**setup_kwargs)
