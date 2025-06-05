FROM public.ecr.aws/docker/library/ubuntu:jammy AS build

ARG vlibras_translator_version=1.1.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0

# Configurar timezone para evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Instalar dependências base e Python 3.10
RUN apt-get update \
    && apt-get install -y \
       build-essential \
       hunspell \
       git \
       git-lfs \
       wget \
       curl \
       libssl-dev \
       zlib1g-dev \
       libbz2-dev \
       libreadline-dev \
       libsqlite3-dev \
       libffi-dev \
       liblzma-dev \
       python3.10 \
       python3.10-dev \
       python3.10-venv \
       python3-pip \
       pkg-config \
    && git lfs install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar links simbólicos para Python
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.10 /usr/bin/python

# Criar ambiente virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip==24 wheel 
RUN pip install --no-cache-dir setuptools==80.9.0

# Copy worker requirements file into the build container
WORKDIR /opt
COPY requirements.txt requirements.txt

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
FROM public.ecr.aws/docker/library/ubuntu:jammy

# Configurar timezone para evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências de runtime
RUN apt-get update \
    && apt-get install -y \
       hunspell \
       build-essential \
       libssl-dev \
       zlib1g-dev \
       libbz2-dev \
       libreadline-dev \
       libsqlite3-dev \
       libffi-dev \
       liblzma-dev \
       wget \
       git \
       git-lfs \
       python3.10 \
       python3.10-dev \
       python3-pip \
       pkg-config \
    && git lfs install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar links simbólicos para Python
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.10 /usr/bin/python

# Set up vlibras-translator-text-core worker
WORKDIR /dist
COPY ./src /dist/

RUN pip install nltk --upgrade
RUN python3 -m nltk.downloader all
RUN pip install Jinja2 --upgrade
RUN pip uninstall -y py
RUN pip install --no-cache-dir --force-reinstall git+https://github.com/diegoramonbs/fairseq.git@vlibras 
RUN pip install --no-cache-dir --force-reinstall numpy==1.26.0

# Tornar o download opcional - se falhar, o modelo será baixado na primeira execução
RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
    echo "Download do modelo falhou durante o build - será baixado na primeira execução"

CMD ["python3", "worker.py"]