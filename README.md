# lidarr-youtube-downloader

Look for missing tracks in your lidarr library and download them from youtube.

# Docker Usage

### docker run
The docker build need the `.git` directory, so be sure to clone the repository.

```
git clone https://github.com/dmzoneill/lidarr-youtube-downloader.git
docker build -t lyd .
# you need to be careful that the path matches the path that lidarr knows
docker run \
   -v /path/to/music:/path/to/music \
   -v /path/to/db/file:/path/to/db/file \   
   -e LIDARR_URL="http://HOST_IP:8686" \
   -e LIDARR_API_KEY="771de60596e946f6b3e5e6f5fb6fd729" \
   -e LIDARR_DB="/path/to/lidarr/lidarr.db" \
   -e LIDARR_MUSIC_PATH="/music" \
   --name lyd lyd
```

# Local Usage

### Requirements
```
dnf/apt install ffmpeg
pip3 install eyed3 youtube-search-python yt-dlp
chmod +x /usr/bin/yt-dlp
```

### Install
```
pip3 install lidarr-youtube-downloader
```

### Config
```
export LIDARR_URL="http://127.0.0.3:8686"
export LIDARR_API_KEY="771de60596e946f6b3e5e6f5fb6fd729" # your key
export LIDARR_DB="/path/to/lidarr/lidarr.db"
export LIDARR_MUSIC_PATH="/music"
```

### Usage
```
lyd
```

# Sample output
```
Album: 34/545   Track: 71/226
================================================================================

    Path           : /music/The Beatles
    Artist         : The Beatles
    Album          : The Beatles
    Track          : Norwegian Wood (This Bird Has Flown)
    Genre          : Acoustic Rock
    Date           : 1988
    CD Count       : 16
    CD No          : 6
    Track No       : 2/12

    Youtube search
    ========================================
        
        Best title: The Beatles - Norwegian Wood (This Bird Has Flown)
        Best match: 1.0
        
        Selected https://www.youtube.com/watch?v=W15_1kE08Gc

    yt-dlp
    ========================================

        yt-dlp
            --no-progress
            -x
            --audio-format mp3 "https://www.youtube.com/watch?v=W15_1kE08Gc"
            -o 
            "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"


        Downloaded successfully

        [youtube] W15_1kE08Gc: Downloading webpage
        [youtube] W15_1kE08Gc: Downloading MPD manifest
        [download] Destination: /music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3
        [download] Download completed
        [ffmpeg] Correcting container in "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"
        [ffmpeg] Post-process file /music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3 exists, skipping

    Ffmpeg
    ========================================

        ffmpeg -i "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"
            -metadata artist="The Beatles"
            -metadata year="1988"
            -metadata title="Norwegian Wood (This Bird Has Flown)"
            -metadata album="The Beatles"
            -metadata track="2"
            -metadata genre="Acoustic Rock"
            -hide_banner
            -loglevel error
            "/music/The Beatles/The Beatles/The Beatles - The Beatles - Norwegian Wood (This Bird Has Flown).mp3"

        ffmpeg added mp3 tag      

```
