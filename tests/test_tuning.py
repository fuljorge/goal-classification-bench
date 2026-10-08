from __future__ import annotations

from collections import Counter

from goalbench.data import Goal
from goalbench.pipeline import Params
from goalbench.tuning import GRID_A_WITH_ZERO, Scored, assign_folds, fit_params, nll


def _goals() -> list[Goal]:
    return [
        Goal(f"g{i}", f"G{i}", f"goal {i}", tuple(f"e{i}-{j}" for j in range(10)), ("t",))
        for i in range(3)
    ]


def test_folds_are_balanced_per_goal_and_seeded() -> None:
    goals = _goals()
    folds = assign_folds(goals, seed=7)
    for goal in goals:
        counts = Counter(folds[(goal.key, i)] for i in range(10))
        assert counts == {f: 2 for f in range(5)}
    assert folds == assign_folds(goals, seed=7)
    assert folds != assign_folds(goals, seed=8)


def _items(informative_sims: bool) -> list[Scored]:
    items = []
    for i in range(30):
        truth = f"g{i % 3}"
        keys = ["g0", "g1", "g2"]
        sims = {k: (0.9 if k == truth else 0.1) if informative_sims else 0.5 for k in keys}
        probabilities = {k: 1 / 3 for k in keys}  # an uninformative classifier
        items.append(Scored(truth, keys, sims, probabilities))
    return items


def test_fit_relies_on_similarity_when_the_classifier_is_uninformative() -> None:
    params = fit_params(_items(True), GRID_A_WITH_ZERO)
    assert params.b > 0
    assert nll(_items(True), params) < nll(_items(True), Params(a=1, b=0))


def test_missing_true_goal_costs_log_eps() -> None:
    item = Scored("g9", ["g0", "g1"], {"g0": 0.5, "g1": 0.4}, {"g0": 0.5, "g1": 0.5})
    assert nll([item], Params()) > 13
