# lidarr-youtube-downloader

Look for missing tracks in your lidarr library and download them from youtube.

# Docker Usage

### Config
```
vim env
```

### docker run
```
docker build -t lys .
# you need to be careful that the path matches the path that lidarr knows
docker run \
   -v /path/to/music:/path/to/music \
   -v /path/to/db/file:/path/to/db/file \   
   --name lys --env-file env lys 
```

# Local Usage

### Requirements
```
dnf/apt install ffmpeg
sudo curl https://youtube-dl.org/downloads/latest/youtube-dl -o /usr/bin/youtube-dl
chmod +x /usr/bin/youtube-dl
pip3 install eyed3 youtube-search-python
```

### Config
```
export LIDARR_URL="http://127.0.0.1:8686"
export LIDARR_API_KEY="771de60596e946f6b3e5e6f5fb6fd729" # your key
export LIDARR_DB="/path/to/lidarr/lidarr.db"
export LIDARR_MUSIC_PATH="/music"
```

### Usage
```
python3 lidarr-youtube-downloader.py
```

# Sample output
```
....
........
3706
================================================================================
Path           : /music/The Box Tops
Artist         : The Box Tops
Album          : Cry Like a Baby
Track          : I'm the One for You
Genre          : Pop
Date           : 1968
CD Count       : 1
CD No          : 1
Track No       : 3/12

youtube search
========================================
Best match: 0.927536231884058

youtube-dl
========================================
youtube-dl
 --no-progress
 -x
 --audio-format mp3 "https://www.youtube.com/watch?v=laMH6ZdnOpQ"
 -o 
 "/music/The Box Tops/Cry Like a Baby/The Box Tops - Cry Like a Baby - I'm the One for You.mp3"

ffmpeg
========================================
ffmpeg -i "/music/The Box Tops/Cry Like a Baby/The Box Tops - Cry Like a Baby - I'm the One for You.mp3"
 -metadata artist="The Box Tops"
 -metadata year="1968"
 -metadata title="I'm the One for You"
 -metadata album="Cry Like a Baby"
 -metadata track="3"
 -metadata genre="Pop"
 -hide_banner
 -loglevel error
 "/music/The Box Tops/Cry Like a Baby/The Box Tops - Cry Like a Baby - I'm the One for You.mp3"

Downloaded successfully
Added mp3 tag
Updated the db

.....
.......

```
