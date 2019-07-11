FROM python:3.6-stretch

RUN apt-get -y update && apt-get -y install --reinstall build-essential && apt-get -y install --reinstall make

#RUN apt-get -y install libpq-dev libssl-dev openssl libffi-dev zlib1g-dev && apt-get install -y python3-pip python3-dev

ADD worker translator-video-worker/

WORKDIR translator-video-worker/

RUN make install

ENTRYPOINT make start || watch -n 120 "find /video/ -name "*.mp4" -mmin +730 -delete"
