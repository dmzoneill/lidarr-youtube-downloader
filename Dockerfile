FROM ubuntu
RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y ffmpeg python3 curl python3-pip python-is-python3
RUN python3 -m pip install --no-deps -U yt-dlp
RUN mv /usr/local/bin/yt-dlp /usr/bin/youtube-dl
RUN chmod +x /usr/bin/youtube-dl
RUN pip3 install requests eyed3 youtube-search-python numpy typer
COPY lidarr_youtube_downloader/lyd.py /
COPY lidarr_youtube_downloader/view/ /view
CMD ["python3", "-u", "/lyd.py"]
