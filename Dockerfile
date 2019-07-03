FROM ubuntu:18.04

RUN apt-get update && apt-get install --yes --reinstall build-essential python3 && apt-get install --reinstall make

ADD worker /worker/

WORKDIR /worker/

#RUN ./preinstall.sh

RUN make install

ENTRYPOINT make start

