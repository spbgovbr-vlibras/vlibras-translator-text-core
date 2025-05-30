FROM public.ecr.aws/docker/library/archlinux:latest AS build

ARG vlibras_translator_version=1.1.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0

# Instalar dependências base e compilar Python 3.10
RUN pacman -Syu --noconfirm \
    && pacman -S --noconfirm \
       base-devel \
       hunspell \
       git \
       wget \
       curl \
       openssl \
       zlib \
       bzip2 \
       readline \
       sqlite \
       libffi \
       xz \
    && pacman -Scc --noconfirm

# Compilar e instalar Python 3.10.17 do código fonte (mesma versão da imagem original)
RUN cd /tmp \
    && wget https://www.python.org/ftp/python/3.10.17/Python-3.10.17.tgz \
    && tar -xzf Python-3.10.17.tgz \
    && cd Python-3.10.17 \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j$(nproc) \
    && make altinstall \
    && cd / && rm -rf /tmp/Python-3.10.17* \
    && ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3 \
    && /usr/local/bin/python3.10 -m ensurepip --upgrade

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip==24 wheel 
RUN pip install --no-cache-dir setuptools==80.9.0

# Copy worker requirements file into the build container
WORKDIR /opt
COPY requirements.txt requirements.txt

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip==24
RUN pip install --no-cache-dir setuptools==80.9.0

RUN pip3 install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu \
  # vlibras-translator-text-core worker requirements
  && pip install --no-cache-dir -r requirements.txt

# vlibras-translator and vlibras-number
RUN pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-number==${vlibras_number_version} \
  && pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "vlibras-translator[neural]"==${vlibras_translator_version} \
  && pip install --no-cache-dir numpy==1.24.2 \ 
  && pip install --no-cache-dir git+https://github.com/diegoramonbs/fairseq.git@vlibras

# Second stage
FROM public.ecr.aws/docker/library/archlinux:latest

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências de runtime e Python 3.10
RUN pacman -Syu --noconfirm --needed \
    && pacman -S --noconfirm --needed \
       hunspell \
       base-devel \
       openssl \
       zlib \
       bzip2 \
       readline \
       sqlite \
       libffi \
       xz \
       wget \
    && pacman -Scc --noconfirm \
    && rm -rf /var/cache/pacman/pkg/*

# Compilar e instalar Python 3.10.17 do código fonte (runtime - mesma versão da imagem original)
RUN cd /tmp \
    && wget https://www.python.org/ftp/python/3.10.17/Python-3.10.17.tgz \
    && tar -xzf Python-3.10.17.tgz \
    && cd Python-3.10.17 \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j$(nproc) \
    && make altinstall \
    && cd / && rm -rf /tmp/Python-3.10.17* \
    && ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3

# Set up vlibras-translator-text-core worker
WORKDIR /dist
COPY ./src /dist/

RUN pip install nltk --upgrade
RUN python3 -m nltk.downloader all

# Tornar o download opcional - se falhar, o modelo será baixado na primeira execução
RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
    echo "Download do modelo falhou durante o build - será baixado na primeira execução"
CMD ["python3", "worker.py"]