"""Two-stage pipeline: embedding shortlist, then a calibrated combination with the classifier.

    s_g  = max_e cos(m, e)                     similarity of message m to goal g's examples
    P(g) = softmax_g((a * log max(p_g, EPS) + b * s_g) / T)   over the shortlist

The prediction is argmax_g P(g), which does not depend on T; T only calibrates.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

EPS = 1e-6
SHORTLIST = 10
OptionOrder = Literal["similarity", "reversed", "random"]
ORDERS: tuple[OptionOrder, ...] = ("similarity", "reversed", "random")


@dataclass(frozen=True)
class Params:
    a: float = 1.0
    b: float = 1.0
    temperature: float = 1.0


def similarity(message: NDArray[np.float32], examples: NDArray[np.float32]) -> float:
    """Highest cosine to the examples (vectors are unit-norm)."""
    if examples.size == 0:
        return 0.0
    return float(np.max(examples @ message))


def shortlist(scores: dict[str, float], limit: int = SHORTLIST) -> list[str]:
    """The `limit` most similar goals, by decreasing similarity (ties by key)."""
    return sorted(scores, key=lambda k: (-scores[k], k))[:limit]


def order_options(keys: list[str], order: OptionOrder, rng: random.Random) -> list[str]:
    """Order in which the shortlist is presented to the classifier.

    `similarity` is what a production pipeline does naturally; it puts the most similar goal
    first, so a classifier with a position prior is rewarded. `reversed` and `random` are the
    controls for that bias.
    """
    if order == "similarity":
        return list(keys)
    if order == "reversed":
        return list(reversed(keys))
    shuffled = list(keys)
    rng.shuffle(shuffled)
    return shuffled


def combine(
    probabilities: dict[str, float], sims: dict[str, float], keys: list[str], params: Params
) -> dict[str, float]:
    temperature = max(params.temperature, 1e-3)
    scores = {
        k: (params.a * math.log(max(probabilities.get(k, 0.0), EPS)) + params.b * sims.get(k, 0.0))
        / temperature
        for k in keys
    }
    top = max(scores.values())
    exps = {k: math.exp(v - top) for k, v in scores.items()}
    total = sum(exps.values())
    return {k: v / total for k, v in exps.items()}


def argmax(values: dict[str, float], keys: list[str]) -> str:
    """Highest value; ties go to the earliest key in `keys`."""
    return max(keys, key=lambda k: (values.get(k, 0.0), -keys.index(k)))
