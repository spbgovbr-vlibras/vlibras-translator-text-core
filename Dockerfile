# ==============================
# STAGE: BUILD
# ==============================
FROM public.ecr.aws/docker/library/ubuntu:24.04 AS build

ARG vlibras_translator_version=1.3.0b4
ARG torch_version=2.8.0

# ------------------------------
# System deps
# ------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc-10 g++-10 \
    hunspell git wget curl ca-certificates unzip \
    libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev libffi-dev \
    liblzma-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libgdbm-compat-dev \
    git-lfs \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 100 \
    && git lfs install \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Python build (fixo e isolado)
# ------------------------------
RUN cd /tmp \
    && wget -q https://www.python.org/ftp/python/3.10.17/Python-3.10.17.tgz \
    && tar -xzf Python-3.10.17.tgz \
    && cd Python-3.10.17 \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j"$(nproc)" \
    && make altinstall \
    && ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3 \
    && python3 -m ensurepip --upgrade \
    && rm -rf /tmp/Python-3.10.17*

# ------------------------------
# Virtualenv
# ------------------------------
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip==24 wheel setuptools==80.9.0

# ------------------------------
# Base libs (ordem CRÍTICA)
# ------------------------------
RUN pip install --no-cache-dir numpy==1.26.0

WORKDIR /opt
COPY requirements.txt .

# Torch primeiro (ABI)
RUN pip install --no-cache-dir torch==${torch_version} \
    --index-url https://download.pytorch.org/whl/cpu

# Requirements depois
RUN pip install --no-cache-dir -r requirements.txt

# VLibras
RUN pip install --no-cache-dir \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    vlibras-number==${vlibras_number_version}

RUN pip install --no-cache-dir \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    "vlibras-translator[neural]"==${vlibras_translator_version}

# Base utils
RUN pip install --no-cache-dir --upgrade nltk Jinja2 \
    && pip uninstall -y py

# Fairseq (força rebuild com numpy correto)
RUN pip install --no-cache-dir --force-reinstall \
    git+https://github.com/diegoramonbs/fairseq.git@vlibras

# Fix final de dependências (fairseq costuma bagunçar)
RUN pip install --no-cache-dir --force-reinstall \
    numpy==1.26.0 \
    joblib==1.2.0 \
    nltk==3.9.3

# ------------------------------
# NLTK DATA (SEM downloader)
# ------------------------------
ENV NLTK_DATA=/usr/local/share/nltk_data

RUN mkdir -p $NLTK_DATA/corpora \
    && wget -q https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip \
    -O /tmp/wordnet.zip \
    && unzip /tmp/wordnet.zip -d $NLTK_DATA/corpora \
    && rm /tmp/wordnet.zip

# ==============================
# STAGE: RUNTIME
# ==============================
FROM public.ecr.aws/docker/library/ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# Runtime deps (mínimo necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    hunspell git wget curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev libffi-dev \
    liblzma-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libgdbm-compat-dev \
    git-lfs \
    && git lfs install \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar runtime pronto
COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local /usr/local

ENV PATH="/opt/venv/bin:$PATH"
ENV NLTK_DATA=/usr/local/share/nltk_data

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
    && python3 -c "import os, pathlib, urllib.request, zipfile; root = pathlib.Path(os.environ['NLTK_DATA']) / 'corpora'; root.mkdir(parents=True, exist_ok=True); archive = root / 'wordnet.zip'; urllib.request.urlretrieve(os.environ['NLTK_WORDNET_URL'], archive); zipfile.ZipFile(archive).extractall(root)"

FROM public.ecr.aws/docker/library/ubuntu:24.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/share/nltk_data \
    PATH=/opt/venv/bin:$PATH

WORKDIR /dist

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ca-certificates git git-lfs python3 \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local/share/nltk_data /usr/local/share/nltk_data
COPY ./src /dist/

RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || true

CMD ["python", "worker.py"]
