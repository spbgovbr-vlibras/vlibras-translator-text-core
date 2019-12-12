FROM python:3.6-slim-stretch as build

RUN mkdir /requirements
WORKDIR /requirements

COPY requirements.txt requirements.txt

RUN apt-get update \
  && mkdir -vp /usr/share/man/man1 \
  && apt-get install -y gcc g++ default-jdk libhunspell-dev \
  && apt-get autoremove && apt-get clean \
  && pip install --no-cache-dir Cython \
  && pip install --no-cache-dir --install-option="--prefix=/requirements" -r requirements.txt

FROM python:3.6-slim-stretch

RUN apt-get update \
  && mkdir -vp /usr/share/man/man1 \
  && apt-get install -y default-jre libhunspell-dev \
  && apt-get autoremove && apt-get clean

COPY --from=build /requirements /usr/local
COPY src/ dist/

# Remove after vlibras_deeplearning oficial release and put on 'build' stage
RUN apt-get install -y curl git \
  && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
  && apt-get install -y git-lfs && git lfs install \
  && apt-get autoremove && apt-get clean \
  && pip install --no-cache-dir Cython \
  && pip install --no-cache-dir --index-url https://test.pypi.org/simple/ vlibras_deeplearning --extra-index-url https://pypi.org/simple/ \
  && vlibras-translate -r "load" && vlibras-translate -n "load"

WORKDIR /dist

ENV CORE_CONFIG_FILE /dist/config/settings.ini
ENV LOGGER_CONFIG_FILE /dist/config/logging.ini

CMD ["python", "worker.py"]
