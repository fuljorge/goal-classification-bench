"""In-process fakes for the embedding server and the System One classifier."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

import httpx

DIM = 64


def bag_of_words(text: str) -> list[float]:
    vector = [0.0] * DIM
    for word in text.lower().split():
        vector[int(hashlib.sha256(word.encode()).hexdigest(), 16) % DIM] += 1.0
    return vector if any(vector) else [1.0] + [0.0] * (DIM - 1)


def embeddings_transport(calls: list[int] | None = None) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        if calls is not None:
            calls.append(len(body["input"]))
        data = [{"index": i, "embedding": bag_of_words(t)} for i, t in enumerate(body["input"])]
        return httpx.Response(200, json={"data": data})

    return httpx.MockTransport(handler)


Policy = Callable[[str, list[str]], dict[str, float]]


def first_option(_message: str, keys: list[str]) -> dict[str, float]:
    """A classifier with a pure position prior: always the first presented option."""
    return {k: (0.9 if i == 0 else 0.1 / (len(keys) - 1)) for i, k in enumerate(keys)}


def classifier_transport(policy: Policy, token: str | None = None) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if token and request.headers.get("authorization") != f"Bearer {token}":
            return httpx.Response(401)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "device": "fake"})
        body: dict[str, Any] = json.loads(request.content)
        question = body["questions"]["goal"]
        keys = list(question["criteria"])
        probabilities = policy(body["state"]["body"], keys)
        choice = max(keys, key=lambda k: probabilities[k])
        answer = {"type": "choice", "choice": choice, "probabilities": probabilities}
        return httpx.Response(200, json={"answers": {"goal": answer}})

    return httpx.MockTransport(handler)
