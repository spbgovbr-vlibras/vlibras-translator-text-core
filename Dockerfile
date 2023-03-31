FROM python:3.10-slim-bullseye AS build

ARG vlibras_translate_version=1.3.0rc1
ARG vlibras_deeplearning_version=1.3.0rc1
ARG torch_version=1.11.0

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip wheel

# Copy worker requirements file into the build container
WORKDIR /opt
COPY requirements.txt requirements.txt

RUN apt-get update \
  # System requirements for vlibras-translate
  && apt-get install -y --no-install-recommends build-essential libhunspell-dev \
  # PyTorch installed separately so we can use the CPU version instead
  && pip3 install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu \
  # vlibras-translator-text-core worker requirements
  && pip install --no-cache-dir -r requirements.txt

# vlibras-translate and vlibras-deeplearning
RUN pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-translate==${vlibras_translate_version} \
    && pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-deeplearning==${vlibras_deeplearning_version}

# Second stage
FROM python:3.10-slim-bullseye

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# System requirements for vlibras-translate
RUN apt-get update \
  && apt-get install -y --no-install-recommends default-jre libhunspell-dev git-lfs \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up vlibras-translator-text-core worker
WORKDIR /dist
COPY src/ /dist/
ENV CORE_CONFIG_FILE="/dist/config/settings.ini"
ENV LOGGER_CONFIG_FILE="/dist/config/logging.ini"

RUN vlibras-translate -n "Essa tradução irá forçar o download de arquivos externos adicionais."
CMD ["python3", "worker.py"]
