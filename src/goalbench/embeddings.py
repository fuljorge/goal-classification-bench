"""Embeddings from any OpenAI-compatible `/embeddings` endpoint, L2-normalised and cached.

The cache stores one vector per (model, instruction, text), so a run can be repeated (other
seeds, other option orders, other classifiers) without calling the embedding server again,
and the exact vectors used in a published run can be shipped with it.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import httpx
import numpy as np
from numpy.typing import NDArray

# Instruction prefixes per model family (matched by substring of the model id).
INSTRUCTIONS: tuple[tuple[str, str], ...] = (
    ("qwen3-embedding", "Instruct: Identify the customer's goal in this message\nQuery: "),
    ("nomic-embed", "classification: "),
)
BATCH = 64

Vectors = NDArray[np.float32]


def instruction_for(model: str) -> str:
    lowered = model.lower()
    return next((prefix for family, prefix in INSTRUCTIONS if family in lowered), "")


def _key(model: str, instruction: str, text: str) -> str:
    return hashlib.sha256(f"{model}\x00{instruction}\x00{text}".encode()).hexdigest()


class EmbeddingClient:
    def __init__(
        self,
        url: str,
        model: str,
        *,
        api_key: str | None = None,
        cache_path: Path | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.url = url
        self.model = model
        self.instruction = instruction_for(model)
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = client or httpx.Client(timeout=120)
        self.cache_path = cache_path
        self.cache: dict[str, Vectors] = {}
        if cache_path is not None and cache_path.exists():
            with np.load(cache_path) as stored:
                self.cache = {k: stored[k] for k in stored.files}

    def embed(self, texts: list[str]) -> Vectors:
        keys = [_key(self.model, self.instruction, t) for t in texts]
        missing = list(
            dict.fromkeys(t for t, k in zip(texts, keys, strict=True) if k not in self.cache)
        )
        for start in range(0, len(missing), BATCH):
            chunk = missing[start : start + BATCH]
            response = self.client.post(
                self.url,
                headers=self.headers,
                json={"model": self.model, "input": [self.instruction + t for t in chunk]},
            )
            response.raise_for_status()
            data = sorted(response.json()["data"], key=lambda d: d.get("index", 0))
            for text, item in zip(chunk, data, strict=True):
                vector = np.asarray(item["embedding"], dtype=np.float32)
                unit = (vector / np.linalg.norm(vector)).astype(np.float32)
                self.cache[_key(self.model, self.instruction, text)] = unit
        if missing and self.cache_path is not None:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(self.cache_path, **self.cache)  # type: ignore[arg-type]
        return np.stack([self.cache[k] for k in keys])
