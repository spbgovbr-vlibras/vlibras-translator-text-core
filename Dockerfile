FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime as build


COPY requirements.txt requirements.txt

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

RUN apt-get update \
  && mkdir -vp /usr/share/man/man1 \
  && apt-get install -y git gcc g++  openjdk-8-jdk libhunspell-dev \
  && apt-get autoremove && apt-get clean \
#  && pip3 install -U pip \
  && pip install Cython \
  && pip install -r requirements.txt 
  # && pip install schedule==1.1.0

RUN git clone https://github.com/pytorch/fairseq \
    && pip install ./fairseq/

RUN pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-translate==1.2.2rc1 \
    && pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-deeplearning==1.2.2rc2

RUN  vlibras-translate -r "load" && vlibras-translate -n "load"

FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN pip install --upgrade pip

RUN apt-get update \
  && mkdir -vp /usr/share/man/man1 \
  && apt-get install -y gcc g++ curl git openjdk-8-jdk libhunspell-dev \
  && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
  && apt-get install -y git-lfs && git lfs install \
  && apt-get autoremove && apt-get clean

WORKDIR /dist

COPY --from=build /opt/venv /opt/venv
#COPY --from=build /root/.cache /root/.cache
#COPY --from=build /root/.local /root/.local
#COPY --from=build /wheels /wheels
COPY src/ /dist/

ENV PATH="/opt/venv/bin:$PATH"

ENV CORE_CONFIG_FILE /dist/config/settings.ini

ENV LOGGER_CONFIG_FILE /dist/config/logging.ini

RUN  vlibras-translate -r "load" && vlibras-translate -n "load"

CMD ["python", "worker.py"]
