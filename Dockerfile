FROM public.ecr.aws/docker/library/ubuntu:20.04 AS build

ARG vlibras_translator_version=1.2.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++-10 \
    hunspell git wget curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev libffi-dev \
    liblzma-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libgdbm-compat-dev \
    git-lfs \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 100 \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 \
    && git lfs install \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cd /tmp \
    && wget https://www.python.org/ftp/python/3.10.17/Python-3.10.17.tgz \
    && tar -xzf Python-3.10.17.tgz \
    && cd Python-3.10.17 \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j"$(nproc)" \
    && make altinstall \
    && cd / && rm -rf /tmp/Python-3.10.17* \
    && ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3 \
    && python3 -m ensurepip --upgrade

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip==24 wheel setuptools==80.9.0

# ✅ NUMPY FIXADO PRIMEIRO — antes de qualquer pacote que compile contra ele
RUN pip install --no-cache-dir "numpy==1.26.0"

WORKDIR /opt
COPY requirements.txt requirements.txt

# ✅ Torch antes do spaCy/thinc, para garantir ABI consistente
RUN pip install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu

# ✅ requirements.txt depois do numpy e torch já fixados
RUN pip install --no-cache-dir -r requirements.txt

# ✅ vlibras packages depois — thinc/spaCy vão usar o numpy já instalado
RUN pip install --no-cache-dir \
        --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple \
        vlibras-number==${vlibras_number_version}

RUN pip install --no-cache-dir \
        --index-url https://test.pypi.org/simple/ \
        --extra-index-url https://pypi.org/simple \
        "vlibras-translator[neural]"==${vlibras_translator_version}

RUN pip install --no-cache-dir --upgrade nltk Jinja2 \
    && pip uninstall -y py

# ✅ fairseq por último — força recompilação já com numpy 1.26 no ambiente
RUN pip install --no-cache-dir --force-reinstall \
        git+https://github.com/diegoramonbs/fairseq.git@vlibras

# ✅ Verificação explícita de compatibilidade ainda no build stage
RUN python3 -c "import numpy; import thinc; import spacy; print('Compatibilidade OK')"

RUN python3 -m nltk.downloader wordnet

# ------------------------------
# Stage final (runtime)
# ------------------------------
FROM public.ecr.aws/docker/library/ubuntu:20.04

# Copiar venv e python compilado do build (Vem pronto, sem necessidade de mexer com pip aqui)
COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local /usr/local

ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências de runtime do sistema operacional
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    hunspell git wget curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev libffi-dev \
    liblzma-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libgdbm-compat-dev \
    git-lfs \
    && git lfs install \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /dist
COPY ./src /dist/

RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
    echo "Download do modelo falhou durante o build - será baixado na primeira execução"

CMD ["python3", "worker.py"]