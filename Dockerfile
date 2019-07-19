FROM python:3.6-stretch

RUN apt-get -y update \
&& apt-get -y install --reinstall build-essential \
&& apt-get -y install --reinstall make

ADD worker translator-video-worker/

WORKDIR translator-video-worker/

RUN make install

ENTRYPOINT make start || watch -n 120 "find /video/ -name "*.mp4" -mmin +730 -delete"
