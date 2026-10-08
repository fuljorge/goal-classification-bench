# syntax=docker/dockerfile:1.10
# laya-serve with pinned versions, multilingual checkpoint preloaded.
#
#   GPU, CUDA 13 (Blackwell; driver >= 580):  docker build -t goalbench-laya servers/laya
#   GPU, CUDA 12.6 (older drivers):            docker build --build-arg TORCH_INDEX=cu126 -t goalbench-laya servers/laya
#   CPU:                                       docker build --build-arg TORCH_INDEX=cpu -t goalbench-laya:cpu servers/laya

FROM python:3.12-slim-bookworm@sha256:54c85f3c47607a77f32adec749d3c81d1348bf25833671f512b26a9b6d778cb3

ARG TORCH_INDEX=cu130
ARG TORCH_VERSION=2.14.0

RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --create-home --home-dir /home/app app

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONUNBUFFERED=1
RUN pip install --index-url "https://download.pytorch.org/whl/${TORCH_INDEX}" "torch==${TORCH_VERSION}"
COPY requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt && pip uninstall -y setuptools wheel

ENV LAYA_HOST=0.0.0.0 \
    LAYA_PORT=8300 \
    LAYA_MODELS=multilingual \
    LAYA_DEFAULT_MODEL=multilingual \
    LAYA_PRELOAD=1 \
    LAYA_MAX_LOADED=1 \
    LAYA_LOG_LEVEL=warning \
    HF_HOME=/home/app/.cache/huggingface

USER app
VOLUME ["/home/app/.cache/huggingface"]
EXPOSE 8300
HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8300/health', timeout=4)"]

# LAYA_API_KEY comes from the environment.
CMD ["laya-serve"]
