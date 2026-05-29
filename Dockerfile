# ==============================
# STAGE: BUILD
# ==============================
FROM public.ecr.aws/docker/library/ubuntu:20.04 AS build

ARG DEBIAN_FRONTEND=noninteractive
ARG vlibras_translator_version=1.2.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0

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
    && wget -q https://github.com/nltk/nltk_data/raw/gh-pages/packages/corpora/wordnet.zip \
    -O /tmp/wordnet.zip \
    && unzip /tmp/wordnet.zip -d $NLTK_DATA/corpora \
    && rm /tmp/wordnet.zip

# ==============================
# STAGE: RUNTIME
# ==============================
FROM public.ecr.aws/docker/library/ubuntu:20.04

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
COPY ./src /dist/

# Pré-download opcional (não quebra build)
RUN vlibras-translator -n "warmup" || true

CMD ["python3", "worker.py"]
