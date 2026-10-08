"""Collect raw observations for one run: one classifier, one option order, one seed.

Nothing is aggregated here. For every phrase the run stores the similarity to every goal,
the shortlist, the order in which options were presented, the classifier's distribution and
the request latency, so that every condition and statistic in `report` is recomputed offline
from these files and nothing depends on a second call to the servers.

    <out>/<label>__<embedding model>__<order>__seed<seed>/
        run.json      configuration, versions, dataset hash, classifier /health
        items.jsonl   one line per phrase (split "cv" = examples in cross-validation,
                      split "test" = held-out test phrases)
"""

from __future__ import annotations

import hashlib
import json
import platform
import random
import re
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from . import __version__
from .classifier import ChoiceClient
from .data import Goal
from .embeddings import EmbeddingClient, Vectors
from .pipeline import OptionOrder, order_options, shortlist, similarity
from .tuning import FOLDS, assign_folds


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9.-]+", "-", value).strip("-").lower()


def run_dir_name(label: str, embedding_model: str, order: str, seed: int) -> str:
    return f"{_slug(label)}__{_slug(embedding_model)}__{order}__seed{seed}"


def collect(
    goals: list[Goal],
    embedder: EmbeddingClient,
    classifier: ChoiceClient,
    *,
    dataset_path: Path,
    label: str,
    order: OptionOrder,
    seed: int,
    shortlist_size: int,
    out_dir: Path,
    progress: Callable[[int, int], None] | None = None,
) -> Path:
    examples = [(g.key, i, t) for g in goals for i, t in enumerate(g.examples)]
    tests = [(g.key, t) for g in goals for t in g.tests]
    vectors = embedder.embed([t for *_, t in examples] + [t for _, t in tests])
    example_vectors = {(k, i): v for (k, i, _), v in zip(examples, vectors, strict=False)}
    test_vectors = vectors[len(examples) :]

    folds = assign_folds(goals, seed)
    order_rng = random.Random(f"order-{seed}")
    descriptions = {g.key: g.description for g in goals}
    total = len(examples) + len(tests)
    items: list[dict[str, Any]] = []

    def observe(split: str, goal: str, text: str, vector: Vectors, fold: int | None) -> None:
        sims = {}
        for g in goals:
            pool = [
                example_vectors[(g.key, i)]
                for i in range(len(g.examples))
                if fold is None or folds[(g.key, i)] != fold
            ]
            sims[g.key] = similarity(vector, np.array(pool))
        keys = shortlist(sims, shortlist_size)
        presented = order_options(keys, order, order_rng)
        answer = classifier.choose(text, {k: descriptions[k] for k in presented})
        items.append(
            {
                "split": split,
                "goal": goal,
                "text": text,
                "fold": fold,
                "sims": {k: round(v, 6) for k, v in sims.items()},
                "shortlist": keys,
                "presented": presented,
                "probabilities": {k: round(v, 6) for k, v in answer.probabilities.items()},
                "latency_ms": round(answer.latency_ms, 3),
            }
        )
        if progress is not None:
            progress(len(items), total)

    for key, index, text in examples:
        observe("cv", key, text, example_vectors[(key, index)], folds[(key, index)])
    for (key, text), vector in zip(tests, test_vectors, strict=True):
        observe("test", key, text, vector, None)

    try:
        health = classifier.health()
    except Exception as exc:  # the health payload is informative only
        health = {"error": type(exc).__name__}

    target = out_dir / run_dir_name(label, embedder.model, order, seed)
    target.mkdir(parents=True, exist_ok=True)
    meta = {
        "goalbench_version": __version__,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "label": label,
        "dataset": {
            "file": dataset_path.name,
            "sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
            "goals": len(goals),
            "examples": len(examples),
            "tests": len(tests),
        },
        "embedding": {"model": embedder.model, "instruction": embedder.instruction},
        "classifier": {
            "model_field": classifier.model,
            "lang": classifier.lang,
            "instructions": classifier.instructions,
            "health": health,
        },
        "protocol": {
            "shortlist": shortlist_size,
            "option_order": order,
            "seed": seed,
            "folds": FOLDS,
        },
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    (target / "run.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (target / "items.jsonl").open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return target
