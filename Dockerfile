FROM python:3.6-slim-stretch as build

RUN mkdir /requirements
WORKDIR /requirements

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --install-option="--prefix=/requirements" -r requirements.txt

FROM python:3.6-slim-stretch

RUN apt-get update \
  && apt-get install -y ffmpeg xvfb \
  && apt-get autoclean \
  && echo "pcm.!default {\n  type plug\n  slave.pcm \"null\"\n}" | tee /etc/asound.conf

COPY --from=build /requirements /usr/local
COPY src/ daemons/ dist/

WORKDIR /dist

ENV CORE_CONFIG_FILE /dist/config/settings.ini
ENV LOGGER_CONFIG_FILE /dist/config/logging.ini

CMD python worker.py & /bin/bash cleaner.sh
