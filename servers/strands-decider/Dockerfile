# syntax=docker/dockerfile:1.10
# Strands Decider behind the laya-serve interface (server.py), pinned checkpoint.
#
#   GPU, CUDA 13 (Blackwell; driver >= 580):  docker build -t goalbench-decider servers/strands-decider
#   GPU, CUDA 12.6 (older drivers):            docker build --build-arg TORCH_INDEX=cu126 -t goalbench-decider servers/strands-decider
#   CPU (slow, interface checks only):         docker build --build-arg TORCH_INDEX=cpu -t goalbench-decider:cpu servers/strands-decider

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
COPY server.py /opt/app/server.py

# Checkpoint and base model (about 4.7 GB) are downloaded on first start into the cache volume.
ENV DECIDER_HOST=0.0.0.0 \
    DECIDER_PORT=8301 \
    DECIDER_DEVICE=cuda \
    DECIDER_LOG_LEVEL=warning \
    HF_HOME=/home/app/.cache/huggingface \
    PYTHONPATH=/opt/app

USER app
VOLUME ["/home/app/.cache/huggingface"]
EXPOSE 8301
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8301/health', timeout=4)"]

# DECIDER_API_KEY comes from the environment.
CMD ["python", "-m", "server"]
