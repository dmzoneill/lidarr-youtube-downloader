# lidarr-youtube-downloader
Lidar youtube downloader

## Requirements
```
dnf/apt install ffmpeg
sudo curl https://youtube-dl.org/downloads/latest/youtube-dl -o /usr/bin/youtube-dl
chmod +x /usr/bin/youtube-dl
pip3 install eyed3 youtubesearchpython
```

## Config
```
export LIDARR_URL="http://127.0.0.1:8686"
export LIDARR_API_KEY="771de60596e946f6b3e5e6f5fb6fd729" # your key
export LIDARR_DB="/path/to/lidarr/lidarr.db"
export LIDARR_MUSIC_PATH="/music"
```

## Usage
```
python3 lidarr-youtube-search.py
```
