FROM ubuntu:noble
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install  --no-install-recommends -y ffmpeg python3 curl python3-pip python-is-python3 && \
    DEBIAN_FRONTEND=noninteractive apt-get clean && \
    rm -r -f /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache-dir --break-system-packages  --no-deps -U yt-dlp && \
    pip3 install --no-cache-dir --break-system-packages requests eyed3 youtube-search-python typer
COPY lidarr_youtube_downloader/lyd.py /
COPY lidarr_youtube_downloader/view/ /view
CMD ["python3", "-u", "/lyd.py"]
