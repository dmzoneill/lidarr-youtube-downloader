FROM ubuntu:noble
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install  --no-install-recommends -y ffmpeg=7:6.1.1-1ubuntu1 python3=3.12.1-0ubuntu1 curl=8.5.0-2ubuntu2 python3-pip=23.3+dfsg-1 python-is-python3=3.11.4-1 && \
    DEBIAN_FRONTEND=noninteractive apt-get clean && \
    rm -r -f /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache-dir --break-system-packages  --no-deps -U yt-dlp==2024.2.25.232703.dev0 && \
    pip3 install --no-cache-dir --break-system-packages requests==2.27.1 eyed3==0.9.7 youtube-search-python==1.6.6 typer==0.9.0
COPY lidarr_youtube_downloader/lyd.py /
COPY lidarr_youtube_downloader/view/ /view
CMD ["python3", "-u", "/lyd.py"]
