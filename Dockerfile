FROM python:3.6.8-jessie

RUN apt-get update && apt-get install --reinstall build-essential && apt-get install --reinstall make

ADD worker /worker/

WORKDIR /worker/

RUN ./preinstall.sh

ENV HUNPOS_TAGGER "/worker/vlibras-libs/aelius/bin/hunpos-tag"

ENV AELIUS_DATA "/worker/vlibras-libs/aelius/aelius_data"

ENV TRANSLATE_DATA "/worker/vlibras-translate/data"

ENV NLTK_DATA "/worker/vlibras-libs/aelius/nltk_data"

ENV PYTHONPATH "/worker/vlibras-libs/aelius:/worker/vlibras-translate/src:/worker/vlibras-translate/src/Ingles:/worker/vlibras-translate/src/Portugues:/worker/vlibras-translate/src/Espanhol:/worker/vlibras-translate/src/Templates:/worker/vlibras-translate/src/Templates:${PYTHONPATH}"

RUN make install

ENTRYPOINT make start

