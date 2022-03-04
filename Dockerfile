FROM ubuntu
RUN apt update -y
RUN apt upgrade -y
RUN apt install -y ffmpeg python3
RUN curl https://youtube-dl.org/downloads/latest/youtube-dl -o /usr/bin/youtube-dl
RUN chmod +x /usr/bin/youtube-dl
RUN pip3 install eyed3 youtubesearchpython
COPY lidarr-youtube-downloader.py /
CMD ["python3", "/lidarr-youtube-downloader.py"]
