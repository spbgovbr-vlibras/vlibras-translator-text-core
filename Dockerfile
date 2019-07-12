FROM python:3.6.8-jessie

RUN apt-get update && apt-get install -y build-essential && apt-get install -y make

ADD worker translator-text-worker/

WORKDIR translator-text-worker/

RUN make install

ENTRYPOINT make start
