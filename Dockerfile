FROM public.ecr.aws/docker/library/ubuntu:22.04 AS build

ARG vlibras_translator_version=1.1.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0

# Atualizar sistema e instalar dependências base
RUN apt-get update --fix-missing \
    && apt-get install -y --no-install-recommends \
    build-essential \
    hunspell \
    git \
    git-lfs \
    wget \
    curl \
    ca-certificates \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libgdbm-compat-dev \
    && git lfs install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Compilar e instalar Python 3.10.17
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

# Criar ambiente virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar pip, wheel, setuptools
RUN pip install --no-cache-dir --upgrade pip==24 wheel setuptools==80.9.0

# Instalar dependências do projeto
WORKDIR /opt
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-number==${vlibras_number_version} \
    && pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "vlibras-translator[neural]"==${vlibras_translator_version} \
    && pip install --no-cache-dir numpy==1.24.2 \
    && pip install --no-cache-dir --force-reinstall git+https://github.com/diegoramonbs/fairseq.git@vlibras

# ------------------------------
# Stage final (runtime)
# ------------------------------
FROM public.ecr.aws/docker/library/ubuntu:22.04

# Copiar venv e python compilado
COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/local /usr/local

ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências de runtime
RUN apt-get update --fix-missing \
    && apt-get install -y --no-install-recommends \
    hunspell \
    build-essential \
    libssl3 \
    zlib1g \
    libbz2-1.0 \
    libreadline8 \
    sqlite3 \
    libffi8 \
    liblzma5 \
    libncurses5 \
    libgdbm6 \
    libnss3 \
    libgdbm-compat4 \
    wget \
    git \
    git-lfs \
    ca-certificates \
    && git lfs install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar código-fonte do worker
WORKDIR /dist
COPY ./src /dist/

# Instalar NLTK e outros pacotes auxiliares
RUN pip install --no-cache-dir --upgrade nltk Jinja2 \
    && python3 -m nltk.downloader wordnet \
    && pip uninstall -y py \
    && pip install --no-cache-dir --force-reinstall numpy==1.26.0

# Tentativa opcional de baixar modelo
RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
    echo "Download do modelo falhou durante o build - será baixado na primeira execução"

CMD ["python3", "worker.py"]