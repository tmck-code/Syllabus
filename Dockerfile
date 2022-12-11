FROM jupyter/datascience-notebook

WORKDIR /code

USER root

RUN mkdir -p /usr/share/man/man1 \
    && apt update \
    && apt install -y --no-install-recommends \
        python3-dev jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

USER jovyan
ADD requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

