FROM ubuntu
RUN DEBIAN_FRONTEND=noninteractive apt-get update -o Acquire::ForceIPv4=true
RUN DEBIAN_FRONTEND=noninteractive apt-get upgrade -o Acquire::ForceIPv4=true -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -o Acquire::ForceIPv4=true -y ffmpeg python3 curl python3-pip
RUN curl https://youtube-dl.org/downloads/latest/youtube-dl -o /usr/bin/youtube-dl
RUN chmod +x /usr/bin/youtube-dl
RUN pip3 install eyed3 requests numpy youtube-search-python
COPY view /view
COPY lidarr-youtube-downloader.py /
COPY view/ /view
CMD ["python3", "/lidarr-youtube-downloader.py"]
