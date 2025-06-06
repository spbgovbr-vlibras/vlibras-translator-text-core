FROM public.ecr.aws/docker/library/archlinux:latest AS build

ARG vlibras_translator_version=1.1.0rc1
ARG vlibras_number_version=1.0.0
ARG torch_version=2.6.0

# Instalar dependências para compilação
RUN pacman -Syu --noconfirm \
    && pacman -S --noconfirm \
    base-devel \
    hunspell \
    git \
    git-lfs \
    wget \
    curl \
    openssl \
    zlib \
    bzip2 \
    readline \
    sqlite \
    libffi \
    xz \
    && git lfs install \
    && yes | pacman -Scc \
    && rm -rf /var/cache/pacman/pkg/* /root/.cache

# Compilar e instalar Python 3.10.17
RUN cd /tmp \
    && wget https://www.python.org/ftp/python/3.10.17/Python-3.10.17.tgz \
    && tar -xzf Python-3.10.17.tgz \
    && cd Python-3.10.17 \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j"$(nproc)" \
    && make altinstall \
    && ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3 \
    && python3 -m ensurepip --upgrade \
    && cd / && rm -rf /tmp/Python-3.10.17*

# Criar ambiente virtual e instalar dependências
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /opt/requirements.txt
WORKDIR /opt

RUN pip install --no-cache-dir --upgrade pip==24 wheel setuptools==80.9.0 \
    && pip install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    vlibras-number==${vlibras_number_version} \
    "vlibras-translator[neural]==${vlibras_translator_version}" \
    && pip install --no-cache-dir numpy==1.24.2 \
    && pip install --no-cache-dir --force-reinstall git+https://github.com/diegoramonbs/fairseq.git@vlibras

# ------------------------------
# Runtime
# ------------------------------
FROM public.ecr.aws/docker/library/archlinux:latest

# Copiar Python compilado e ambiente virtual
COPY --from=build /usr/local/bin/python3.10 /usr/local/bin/python3.10
COPY --from=build /usr/local/bin/python3 /usr/local/bin/python3
COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=build /usr/local/include/python3.10 /usr/local/include/python3.10
COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Instalar apenas dependências necessárias para execução
RUN pacman -Syu --noconfirm \
    && pacman -S --noconfirm --needed --overwrite "*" \
    hunspell \
    openssl \
    zlib \
    libffi \
    xz \
    git \
    git-lfs \
    wget \
    && git lfs install \
    && yes | pacman -Scc \
    && rm -rf /var/cache/pacman/pkg/* /root/.cache

# Copiar código do projeto
WORKDIR /dist
COPY ./src /dist/

# Instalar pacotes auxiliares
RUN pip install --no-cache-dir --upgrade nltk Jinja2 \
    && python3 -m nltk.downloader wordnet \
    && pip uninstall -y py \
    && pip install --no-cache-dir --force-reinstall numpy==1.26.0

# Baixar modelo (tentativa opcional)
RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais." || \
    echo "Download do modelo falhou durante o build - será baixado na primeira execução"

CMD ["python3", "worker.py"]
