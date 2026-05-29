FROM public.ecr.aws/docker/library/ubuntu:24.04 AS build

ARG vlibras_translator_version=1.3.0b4
ARG torch_version=2.8.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/share/nltk_data \
    NLTK_WORDNET_URL=https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip \
    PATH=/opt/venv/bin:$PATH

WORKDIR /dist

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ca-certificates git git-lfs python3 python3-venv \
    && git lfs install --system \
    && python3 -m venv /opt/venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --upgrade "setuptools>=69" wheel \
    && pip install -r requirements.txt \
    && pip install \
        "joblib==1.2.0" \
        "langdetect==1.0.9" \
        "nltk==3.9.4" \
        "numpy==1.26.0" \
        "rich==13.5.2" \
        "spacy==3.7.5" \
        "subword-nmt==0.3.8" \
        "torch==${torch_version}" \
        --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install \
        --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple \
        "vlibras-translator[neural]==${vlibras_translator_version}" \
    && python3 -m spacy download pt_core_news_md \
    && python3 -c "import os, pathlib, urllib.request, zipfile; root = pathlib.Path(os.environ['NLTK_DATA']) / 'corpora'; root.mkdir(parents=True, exist_ok=True); archive = root / 'wordnet.zip'; urllib.request.urlretrieve(os.environ['NLTK_WORDNET_URL'], archive); zipfile.ZipFile(archive).extractall(root)" \
    && (vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || true)

FROM public.ecr.aws/docker/library/ubuntu:24.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/share/nltk_data \
    PATH=/opt/venv/bin:$PATH

WORKDIR /dist

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local/share/nltk_data /usr/local/share/nltk_data
COPY ./src /dist/

CMD ["python", "worker.py"]
