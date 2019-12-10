FROM python:3.6-slim-stretch as build

RUN mkdir /requirements
WORKDIR /requirements

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --install-option="--prefix=/requirements" -r requirements.txt
RUN echo "pcm.!default {\n  type plug\n  slave.pcm \"null\"\n}" | tee /etc/asound.conf

FROM python:3.6-slim-stretch

RUN apt-get update \
  && apt-get install -y ffmpeg xvfb \
  && apt-get autoclean

COPY --from=build /requirements /usr/local
COPY --from=build /etc/asound.conf /etc
COPY src/ dist

WORKDIR /dist

ENV CORE_CONFIG_FILE /dist/config/settings.ini
ENV LOGGER_CONFIG_FILE /dist/config/logging.ini

CMD ["python", "worker.py"]
