# Manter ubuntu:jammy por questões de segurança
FROM public.ecr.aws/docker/library/ubuntu:jammy AS build

ARG vlibras_translator_version=1.1.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0
ARG python_version=3.10.17

# Set timezone to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

# Install Python 3.10.17 and essential build dependencies (combinado em um RUN)
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    git \
    ca-certificates \
    libhunspell-dev \
    && wget https://www.python.org/ftp/python/${python_version}/Python-${python_version}.tgz \
    && tar xzf Python-${python_version}.tgz \
    && cd Python-${python_version} \
    && ./configure --enable-optimizations --with-ensurepip=install --enable-shared \
    && make -j$(nproc) \
    && make altinstall \
    && cd / \
    && rm -rf Python-${python_version}* \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create symlinks and set up library path
RUN ln -s /usr/local/bin/python3.10 /usr/local/bin/python3 \
    && ln -s /usr/local/bin/python3.10 /usr/local/bin/python \
    && ln -s /usr/local/bin/pip3.10 /usr/local/bin/pip3 \
    && ln -s /usr/local/bin/pip3.10 /usr/local/bin/pip \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/python3.10.conf \
    && ldconfig \
    && python3 -m venv /opt/venv

# Update PATH and install Python packages
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"

# Copy requirements and install all Python dependencies in fewer layers
WORKDIR /opt
COPY requirements.txt .

# Install all packages in one optimized RUN command
RUN pip install --no-cache-dir --upgrade pip==24 wheel setuptools==80.9.0 \
    && pip install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade \
       --index-url https://test.pypi.org/simple/ \
       --extra-index-url https://pypi.org/simple \
       vlibras-number==${vlibras_number_version} \
       "vlibras-translator[neural]"==${vlibras_translator_version} \
       numpy==1.24.2 nltk Jinja2 \
    && python -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context; import nltk; nltk.download('all', quiet=True)" \
    && git config --global http.sslverify false \
    && pip install --no-cache-dir --force-reinstall git+https://github.com/diegoramonbs/fairseq.git@vlibras \
    && pip install --no-cache-dir --force-reinstall numpy==1.26.0 \
    && pip cache purge \
    && find /opt/venv -name "*.pyc" -delete \
    && find /opt/venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -name "*.pyo" -delete

# Runtime stage - imagem final mínima
FROM public.ecr.aws/docker/library/ubuntu:jammy

# Set timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libhunspell-dev \
    git \
    ca-certificates \
    # Runtime libraries needed by Python
    libssl3 \
    libffi8 \
    libbz2-1.0 \
    libreadline8 \
    libsqlite3-0 \
    liblzma5 \
    libncurses6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy Python installation from build stage
COPY --from=build /usr/local/bin/python3.10 /usr/local/bin/python3.10
COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=build /usr/local/lib/libpython3.10.so.1.0 /usr/local/lib/libpython3.10.so.1.0
COPY --from=build /usr/local/include/python3.10 /usr/local/include/python3.10
COPY --from=build /opt/venv /opt/venv
COPY --from=build /etc/ld.so.conf.d/python3.10.conf /etc/ld.so.conf.d/python3.10.conf

# Set up library path and create symlinks
RUN ldconfig \
    && ln -s /usr/local/bin/python3.10 /usr/local/bin/python3 \
    && ln -s /usr/local/bin/python3.10 /usr/local/bin/python \
    && ln -s /usr/local/lib/libpython3.10.so.1.0 /usr/local/lib/libpython3.10.so

# Update PATH (LD_LIBRARY_PATH já configurado via ldconfig)
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"

# Copy application code
WORKDIR /dist
COPY ./src /dist/

# Final cleanup and model download
RUN find /opt/venv -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -name "test" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /opt/venv -name "*.dist-info" -type d -exec rm -rf {}/RECORD {} + 2>/dev/null || true

# Tentar executar vlibras-translator para baixar modelos (opcional)
RUN echo "Tentando executar vlibras-translator para download de modelos..." \
    && (/opt/venv/bin/vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
        /opt/venv/bin/python -m vlibras_translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
        python -c "try: import vlibras_translator; print('vlibras_translator importado com sucesso')" || \
        echo "vlibras-translator não executado durante build - será executado no runtime")

CMD ["python", "worker.py"]