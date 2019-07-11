FROM python:3.6.8-jessie

RUN apt-get update //
 && apt-get install --reinstall build-essential //
 && apt-get install --reinstall make

ADD worker translator-video-worker/

WORKDIR translator-video-worker/

RUN make install

ENTRYPOINT make start
