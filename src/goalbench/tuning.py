"""Fitting (a, b, T) by k-fold cross-validation on the examples only.

Each goal's examples are shuffled with the run seed and dealt round-robin into the folds, so
every fold holds the same number of examples per goal. An example in fold f is scored against
the examples of the other folds only (of every goal), which is how a new message relates to a
goal's stored examples in production.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import product

import numpy as np
from numpy.typing import NDArray

from .data import Goal
from .pipeline import EPS, Params

FOLDS = 5
GRID_A_PLATFORM = (0.5, 1.0, 2.0)
GRID_A_WITH_ZERO = (0.0, 0.5, 1.0, 2.0)
GRID_B = (0.0, 1.0, 2.0, 4.0, 8.0)
GRID_T = (0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0)
MISS_LOGP = float(np.log(EPS))


@dataclass(frozen=True)
class Scored:
    """One phrase as the combination sees it: true goal, shortlist, both signals."""

    truth: str
    keys: list[str]
    sims: dict[str, float]
    probabilities: dict[str, float]


def assign_folds(goals: list[Goal], seed: int, folds: int = FOLDS) -> dict[tuple[str, int], int]:
    """Fold of each example, as {(goal key, example index): fold}."""
    rng = random.Random(seed)
    result: dict[tuple[str, int], int] = {}
    for goal in goals:
        indices = list(range(len(goal.examples)))
        rng.shuffle(indices)
        for position, index in enumerate(indices):
            result[(goal.key, index)] = position % folds
    return result


def _matrices(
    items: list[Scored], width: int
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.bool_], NDArray[np.int64]]:
    n = len(items)
    logp = np.full((n, width), MISS_LOGP)
    sims = np.zeros((n, width))
    mask = np.zeros((n, width), dtype=bool)
    truth = np.full(n, -1, dtype=np.int64)
    for i, item in enumerate(items):
        for j, key in enumerate(item.keys[:width]):
            logp[i, j] = np.log(max(item.probabilities.get(key, 0.0), EPS))
            sims[i, j] = item.sims.get(key, 0.0)
            mask[i, j] = True
            if key == item.truth:
                truth[i] = j
    return logp, sims, mask, truth


def _log_softmax(scores: NDArray[np.float64], mask: NDArray[np.bool_]) -> NDArray[np.float64]:
    masked = np.where(mask, scores, -np.inf)
    top = np.max(masked, axis=1, keepdims=True)
    result: NDArray[np.float64] = masked - (
        top + np.log(np.sum(np.exp(masked - top), axis=1, keepdims=True))
    )
    return result


def nll(items: list[Scored], params: Params) -> float:
    """Mean negative log-likelihood of the true goal; a goal outside the shortlist costs
    log(EPS)."""
    width = max(len(i.keys) for i in items)
    logp, sims, mask, truth = _matrices(items, width)
    log_probs = _log_softmax((params.a * logp + params.b * sims) / params.temperature, mask)
    rows = np.arange(len(items))
    values = np.where(truth >= 0, log_probs[rows, np.maximum(truth, 0)], MISS_LOGP)
    return -float(np.mean(values))


def fit_params(
    items: list[Scored],
    grid_a: tuple[float, ...] = GRID_A_PLATFORM,
    grid_b: tuple[float, ...] = GRID_B,
    grid_t: tuple[float, ...] = GRID_T,
) -> Params:
    """Grid point with the lowest NLL; (a, b) = (0, 0) is skipped (no signal)."""
    best, best_nll = Params(), float("inf")
    for a, b, temperature in product(grid_a, grid_b, grid_t):
        if a == 0 and b == 0:
            continue
        value = nll(items, Params(a=a, b=b, temperature=temperature))
        if value < best_nll - 1e-12:
            best, best_nll = Params(a=a, b=b, temperature=temperature), value
    return best
