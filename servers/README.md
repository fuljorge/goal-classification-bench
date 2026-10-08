# Decider servers

Both deciders are served over the same HTTP interface, the System One API as implemented by
`laya-serve`: `GET /health` and `POST /v1/systemone`, with a Bearer token. `goalbench run`
only needs a base URL and a token.

| Server | Port | Checkpoint | Download | VRAM (bf16) |
|---|---|---|---|---|
| [`laya/`](laya/) | 8300 | `convaiinnovations/laya` / `multilingual` | about 1.3 GB | about 1.5 GB |
| [`strands-decider/`](strands-decider/) | 8301 | `StrandsAgents/strands-decider-2B-hobson-v21` @ `2b52a62` | about 4.7 GB | about 6 GB |

Both fit together on a 16 GB GPU. Measure them **one at a time**, so that one model's load
does not affect the other's latency.

## Tokens

Generate a random token for each server and keep it in an environment variable:

```sh
export LAYA_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
export DECIDER_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

When running the benchmark, pass the matching token in `GOALBENCH_CLASSIFIER_TOKEN`.

## Docker (Linux, or Windows with WSL2 and GPU support)

```sh
docker build -t goalbench-laya servers/laya
docker build -t goalbench-decider servers/strands-decider

docker run -d --name goalbench-laya --gpus all -p 127.0.0.1:8300:8300 \
  -e LAYA_API_KEY=$LAYA_TOKEN -v goalbench-hf:/home/app/.cache/huggingface goalbench-laya
docker run -d --name goalbench-decider --gpus all -p 127.0.0.1:8301:8301 \
  -e DECIDER_API_KEY=$DECIDER_TOKEN -v goalbench-hf:/home/app/.cache/huggingface goalbench-decider
```

The default PyTorch build is `cu130`. Blackwell GPUs (RTX 50xx) require it, and it needs a
driver ≥ 580. For older drivers, use `--build-arg TORCH_INDEX=cu126`. For a CPU-only
interface check, use `--build-arg TORCH_INDEX=cpu` and `-e DECIDER_DEVICE=cpu`; it is slow.

## Without Docker (any OS)

Use one virtual environment per server, because the two packages require different
`transformers` versions:

```sh
uv venv .venv-laya -p 3.12
uv pip install -p .venv-laya --index-url https://download.pytorch.org/whl/cu130 torch==2.14.0
uv pip install -p .venv-laya -r servers/laya/requirements.txt
LAYA_API_KEY=$LAYA_TOKEN LAYA_HOST=127.0.0.1 LAYA_PORT=8300 LAYA_MODELS=multilingual \
  LAYA_DEFAULT_MODEL=multilingual LAYA_PRELOAD=1 LAYA_MAX_LOADED=1 .venv-laya/bin/laya-serve

uv venv .venv-decider -p 3.12
uv pip install -p .venv-decider --index-url https://download.pytorch.org/whl/cu130 torch==2.14.0
uv pip install -p .venv-decider -r servers/strands-decider/requirements.txt
DECIDER_API_KEY=$DECIDER_TOKEN PYTHONPATH=servers/strands-decider \
  .venv-decider/bin/python -m server
```

On Windows, the executables are in `Scripts\` instead of `bin/`. Set `HF_HOME` to choose
where the models are cached.

Both servers listen on `127.0.0.1` by default. Expose them on a network only behind TLS, and
keep the token required.

## Why a wrapper for the Strands Decider

`strands-decider serve` (0.1.0) has no authentication and no batch route.
[`strands-decider/server.py`](strands-decider/server.py) loads the same engine
(`strands_decider.server.create_app`) and adds:

- a Bearer token, compared in constant time;
- `POST /v1/systemone/batch`.

It ignores the Laya-only `lang` field. The wrapper's tests use a fake engine:

```sh
uv run --with fastapi --with httpx --with pytest pytest servers/strands-decider
```
