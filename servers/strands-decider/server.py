"""Strands Decider behind the same HTTP interface as `laya-serve`.

`strands-decider serve` (0.1.0) has no authentication and no batch route. This server loads
the same engine and exposes:

    GET  /health               without token: {"status": "ok"}; with token: model details
    POST /v1/systemone         one state (same body as Laya; "model" and "lang" are ignored)
    POST /v1/systemone/batch   {"states": [...], "questions": {...}} -> {"results": [...]}

Environment variables:
    DECIDER_API_KEY      Bearer token (required unless DECIDER_ALLOW_NO_AUTH=1)
    DECIDER_CHECKPOINT   Hugging Face repo id or local folder
    DECIDER_REVISION     pinned checkpoint revision (Hugging Face commit)
    DECIDER_DEVICE       cuda, cpu, mps or mlx
    DECIDER_ALIAS        name listed in /health "loaded" (default: strands-decider)
    DECIDER_HOST, DECIDER_PORT, DECIDER_LOG_LEVEL
"""

from __future__ import annotations

import hmac
import os
import threading
import time
from collections.abc import Callable
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

DEFAULT_CHECKPOINT = "StrandsAgents/strands-decider-2B-hobson-v21"
DEFAULT_REVISION = "2b52a6235c1b8306bbfa30b00b9d4b74b63a39f5"
MAX_BATCH_STATES = 64

# Takes one request body and returns the Decider answer; raises ValidationError or
# ValueError when the request is invalid.
Evaluate = Callable[[dict[str, Any]], dict[str, Any]]


class BatchRequest(BaseModel):
    states: list[Any] = Field(..., min_length=1, max_length=MAX_BATCH_STATES)
    questions: dict[str, Any] = Field(..., min_length=1)
    model: str | None = None


def build_app(
    evaluate: Evaluate, *, api_key: str | None, alias: str, details: dict[str, Any]
) -> FastAPI:
    """App over `evaluate`; kept apart from model loading so it can be tested without a GPU."""
    app = FastAPI(title="Strands Decider", docs_url=None, redoc_url=None, openapi_url=None)
    # One GPU and one prefix cache: one evaluation at a time.
    lock = threading.Lock()

    def authorized(request: Request) -> bool:
        if api_key is None:
            return True
        scheme, _, token = request.headers.get("authorization", "").partition(" ")
        return scheme.lower() == "bearer" and hmac.compare_digest(token, api_key)

    def require_token(request: Request) -> None:
        if not authorized(request):
            raise HTTPException(status_code=401, detail="invalid or missing token")

    def run(body: dict[str, Any]) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            with lock:
                answer = evaluate(body)
        except (ValidationError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        answer["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return answer

    @app.get("/health")
    def health(request: Request) -> dict[str, Any]:
        if not authorized(request):
            return {"status": "ok"}
        return {"status": "ok", "loaded": [alias], **details}

    @app.post("/v1/systemone", dependencies=[Depends(require_token)])
    def systemone(body: dict[str, Any]) -> JSONResponse:
        return JSONResponse(content=run(body))

    @app.post("/v1/systemone/batch", dependencies=[Depends(require_token)])
    def systemone_batch(body: BatchRequest) -> JSONResponse:
        started = time.perf_counter()
        results = [run({"state": s, "questions": body.questions}) for s in body.states]
        total = {
            name: sum(r.get("usage", {}).get(name, 0) for r in results)
            for name in ("input_tokens", "output_tokens")
        }
        return JSONResponse(
            content={
                "results": results,
                "total_usage": total,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )

    return app


def _load_engine(checkpoint: str, revision: str | None, device: str) -> Any:
    from huggingface_hub import snapshot_download
    from strands_decider import server

    # The checkpoint is pinned; strands-decider 0.1.0 loads its base model (Qwen3.5-2B-Base)
    # from the default branch, without a pinned revision.
    path = checkpoint if os.path.isdir(checkpoint) else snapshot_download(checkpoint, revision=revision)
    server.create_app(path, device=device, model_name=checkpoint.split("/")[-1])
    return server.get_engine()


def main() -> None:
    import uvicorn
    from strands_decider.schema import SystemOneRequest

    api_key = os.environ.get("DECIDER_API_KEY") or None
    if api_key is None and os.environ.get("DECIDER_ALLOW_NO_AUTH") != "1":
        raise SystemExit("Set DECIDER_API_KEY (or DECIDER_ALLOW_NO_AUTH=1 on a local machine).")
    checkpoint = os.environ.get("DECIDER_CHECKPOINT", DEFAULT_CHECKPOINT)
    revision = os.environ.get("DECIDER_REVISION", DEFAULT_REVISION) or None
    alias = os.environ.get("DECIDER_ALIAS", "strands-decider")
    engine = _load_engine(checkpoint, revision, os.environ.get("DECIDER_DEVICE", "cuda"))

    def evaluate(body: dict[str, Any]) -> dict[str, Any]:
        # Extra fields such as "lang" are ignored by the schema; "model" is the server's.
        request = SystemOneRequest.model_validate({**body, "model": engine.cfg.model_name})
        return engine.evaluate(request).model_dump()

    config = engine.model.config
    details = {
        "engine": "strands-decider",
        "model": engine.cfg.model_name,
        "checkpoint": checkpoint,
        "revisions": {alias: revision or "local"},
        "base_model": config.base_model,
        "num_slots": config.num_slots,
        "max_length": config.max_length,
        "device": engine.cfg.device,
    }
    uvicorn.run(
        build_app(evaluate, api_key=api_key, alias=alias, details=details),
        host=os.environ.get("DECIDER_HOST", "127.0.0.1"),
        port=int(os.environ.get("DECIDER_PORT", "8301")),
        workers=1,
        log_level=os.environ.get("DECIDER_LOG_LEVEL", "warning"),
    )


if __name__ == "__main__":
    main()
