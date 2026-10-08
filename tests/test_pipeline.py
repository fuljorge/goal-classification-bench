from __future__ import annotations

import random

import numpy as np

from goalbench.pipeline import Params, argmax, combine, order_options, shortlist, similarity


def test_similarity_is_the_highest_cosine() -> None:
    message = np.array([1.0, 0.0], dtype=np.float32)
    examples = np.array([[0.0, 1.0], [0.6, 0.8]], dtype=np.float32)
    assert similarity(message, examples) == np.float32(0.6)
    assert similarity(message, np.zeros((0, 2), dtype=np.float32)) == 0.0


def test_shortlist_orders_by_similarity_then_key() -> None:
    assert shortlist({"b": 0.5, "a": 0.5, "c": 0.9, "d": 0.1}, 3) == ["c", "a", "b"]


def test_option_orders() -> None:
    keys = [str(i) for i in range(10)]
    assert order_options(keys, "similarity", random.Random(0)) == keys
    assert order_options(keys, "reversed", random.Random(0)) == keys[::-1]
    first = order_options(keys, "random", random.Random(1))
    assert sorted(first) == keys
    assert first == order_options(keys, "random", random.Random(1))


def test_temperature_does_not_change_the_prediction() -> None:
    probabilities = {"x": 0.7, "y": 0.2, "z": 0.1}
    sims = {"x": 0.1, "y": 0.9, "z": 0.2}
    keys = ["x", "y", "z"]
    picks = {
        argmax(combine(probabilities, sims, keys, Params(a=1, b=4, temperature=t)), keys)
        for t in (0.25, 1.0, 3.0)
    }
    assert picks == {"y"}
    assert argmax(combine(probabilities, sims, keys, Params(a=1, b=0)), keys) == "x"


def test_argmax_breaks_ties_towards_the_first_key() -> None:
    assert argmax({"a": 0.5, "b": 0.5}, ["b", "a"]) == "b"
