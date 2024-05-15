FROM python:3.10-slim-bullseye AS build

ARG vlibras_translator_version=1.0.0rc1
ARG vlibras_number_version=1.0.0rc1
ARG torch_version=2.0.0

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip wheel

# Copy worker requirements file into the build container
WORKDIR /opt
COPY requirements.txt requirements.txt

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

RUN apt-get update \
  # System requirements for vlibras-translator
  && apt-get install -y --no-install-recommends build-essential libhunspell-dev \
  # PyTorch installed separately so we can use the CPU version instead
  && pip3 install --no-cache-dir torch==${torch_version} --index-url https://download.pytorch.org/whl/cpu \
  # vlibras-translator-text-core worker requirements
  && pip install --no-cache-dir -r requirements.txt

# vlibras-translator and vlibras-number
RUN pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vlibras-number==${vlibras_number_version} \
  && pip install --no-cache-dir --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "vlibras-translator[neural]"==${vlibras_translator_version}

# Second stage
FROM python:3.10-slim-bullseye

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# System requirements for vlibras-translator
RUN apt-get update \
  && apt-get install -y --no-install-recommends libhunspell-dev git-lfs \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up vlibras-translator-text-core worker
WORKDIR /dist
COPY ./src /dist/

RUN vlibras-translator -n "Essa tradução irá forçar o download de arquivos externos adicionais."
CMD ["python3", "worker.py"]
