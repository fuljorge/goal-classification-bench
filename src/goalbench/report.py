"""Offline analysis of collected runs: conditions, intervals, latency and paired tests."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from itertools import combinations, product
from pathlib import Path
from typing import Any

from .pipeline import Params, argmax, combine
from .stats import mcnemar_exact, percentile, wilson
from .tuning import GRID_A_PLATFORM, GRID_A_WITH_ZERO, GRID_B, Scored, fit_params

CONDITIONS = (
    "shortlist_recall",
    "first_option",
    "embeddings_alone",
    "classifier_alone",
    "fitted_platform_grid",
    "fitted_grid_with_zero",
    "oracle_on_test",
)
DESCRIPTIONS = {
    "shortlist_recall": "true goal is in the shortlist (upper bound of every other row)",
    "first_option": "always pick the first presented option (position baseline)",
    "embeddings_alone": "argmax of the similarity (a = 0)",
    "classifier_alone": "argmax of the classifier distribution (b = 0)",
    "fitted_platform_grid": "(a, b, T) fitted by CV on the examples, a in {0.5, 1, 2}",
    "fitted_grid_with_zero": "(a, b, T) fitted by CV on the examples, a in {0, 0.5, 1, 2}",
    "oracle_on_test": "(a, b) chosen on the test phrases: optimistic ceiling, not a result",
}


@dataclass
class Run:
    path: Path
    meta: dict[str, Any]
    cv: list[dict[str, Any]]
    test: list[dict[str, Any]]

    @property
    def name(self) -> str:
        return self.path.name


@dataclass
class Result:
    hits: int
    n: int
    params: Params | None = None
    correct: list[bool] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        low, high = wilson(self.hits, self.n)
        out: dict[str, Any] = {
            "hits": self.hits,
            "n": self.n,
            "accuracy": self.hits / self.n if self.n else None,
            "wilson95": [low, high],
        }
        if self.params is not None:
            out["params"] = self.params.__dict__
        return out


def load_run(path: Path) -> Run:
    meta = json.loads((path / "run.json").read_text(encoding="utf-8"))
    rows = [
        json.loads(line)
        for line in (path / "items.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    return Run(
        path,
        meta,
        [r for r in rows if r["split"] == "cv"],
        [r for r in rows if r["split"] == "test"],
    )


def _scored(rows: list[dict[str, Any]]) -> list[Scored]:
    return [Scored(r["goal"], r["shortlist"], r["sims"], r["probabilities"]) for r in rows]


def _result(correct: list[bool], params: Params | None = None) -> Result:
    return Result(sum(correct), len(correct), params, correct)


def _with_params(rows: list[dict[str, Any]], params: Params) -> list[bool]:
    return [
        argmax(combine(r["probabilities"], r["sims"], r["shortlist"], params), r["shortlist"])
        == r["goal"]
        for r in rows
    ]


def analyze(run: Run) -> dict[str, Result]:
    test = run.test
    cv = _scored(run.cv)
    platform = fit_params(cv, GRID_A_PLATFORM)
    with_zero = fit_params(cv, GRID_A_WITH_ZERO)
    oracle_grid = [Params(a=a, b=b) for a, b in product(GRID_A_WITH_ZERO, GRID_B) if a or b]
    oracle = max(oracle_grid, key=lambda p: sum(_with_params(test, p)))
    return {
        "shortlist_recall": _result([r["goal"] in r["shortlist"] for r in test]),
        "first_option": _result([r["presented"][0] == r["goal"] for r in test]),
        "embeddings_alone": _result([argmax(r["sims"], r["shortlist"]) == r["goal"] for r in test]),
        "classifier_alone": _result(
            [argmax(r["probabilities"], r["presented"]) == r["goal"] for r in test]
        ),
        "fitted_platform_grid": _result(_with_params(test, platform), platform),
        "fitted_grid_with_zero": _result(_with_params(test, with_zero), with_zero),
        "oracle_on_test": _result(_with_params(test, oracle), oracle),
    }


def position_bias(run: Run) -> dict[str, float]:
    """How often the classifier picks the first presented option, and how often it should."""
    test = run.test
    picked_first = sum(
        argmax(r["probabilities"], r["presented"]) == r["presented"][0] for r in test
    )
    truth_first = sum(r["presented"][0] == r["goal"] for r in test)
    return {"picks_first": picked_first / len(test), "truth_first": truth_first / len(test)}


def latency(run: Run) -> dict[str, float]:
    values = [r["latency_ms"] for r in run.test]
    return {
        "median_ms": statistics.median(values),
        "p95_ms": percentile(values, 0.95),
        "max_ms": max(values),
    }


def summary(run: Run) -> dict[str, Any]:
    results = analyze(run)
    return {
        "run": run.name,
        "label": run.meta["label"],
        "embedding_model": run.meta["embedding"]["model"],
        "option_order": run.meta["protocol"]["option_order"],
        "seed": run.meta["protocol"]["seed"],
        "conditions": {k: v.as_dict() for k, v in results.items()},
        "position_bias": position_bias(run),
        "classifier_latency": latency(run),
    }


def paired(runs: list[Run], condition: str) -> list[dict[str, Any]]:
    """Exact McNemar test between every pair of runs on the same test phrases."""
    analyses = {run.name: analyze(run) for run in runs}
    keys = {run.name: [(r["goal"], r["text"]) for r in run.test] for run in runs}
    out = []
    for first, second in combinations(runs, 2):
        if keys[first.name] != keys[second.name]:
            raise ValueError(f"{first.name} and {second.name} have different test phrases")
        a = analyses[first.name][condition].correct
        b = analyses[second.name][condition].correct
        only_a = sum(x and not y for x, y in zip(a, b, strict=True))
        only_b = sum(y and not x for x, y in zip(a, b, strict=True))
        out.append(
            {
                "condition": condition,
                "first": first.name,
                "second": second.name,
                "only_first_correct": only_a,
                "only_second_correct": only_b,
                "p_value": mcnemar_exact(only_a, only_b),
            }
        )
    return out


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def markdown(summaries: list[dict[str, Any]], tests: list[dict[str, Any]]) -> str:
    lines = [
        "| Run | " + " | ".join(CONDITIONS) + " | picks first | p50 / p95 ms |",
        "|---" * (len(CONDITIONS) + 3) + "|",
    ]
    for s in summaries:
        cells = []
        for condition in CONDITIONS:
            c = s["conditions"][condition]
            low, high = c["wilson95"]
            cell = f"{_pct(c['accuracy'])} [{_pct(low)}, {_pct(high)}]"
            if "params" in c:
                p = c["params"]
                cell += f" (a={p['a']:g}, b={p['b']:g}, T={p['temperature']:g})"
            cells.append(cell)
        lat = s["classifier_latency"]
        lines.append(
            f"| {s['run']} | "
            + " | ".join(cells)
            + f" | {_pct(s['position_bias']['picks_first'])}"
            + f" | {lat['median_ms']:.0f} / {lat['p95_ms']:.0f} |"
        )
    if tests:
        lines += [
            "",
            "| Condition | First | Second | Only first | Only second | McNemar p |",
            "|---|---|---|---|---|---|",
        ]
        for t in tests:
            lines.append(
                f"| {t['condition']} | {t['first']} | {t['second']} | {t['only_first_correct']}"
                f" | {t['only_second_correct']} | {t['p_value']:.4f} |"
            )
    lines += ["", "Conditions:"] + [f"- `{k}`: {v}" for k, v in DESCRIPTIONS.items()]
    return "\n".join(lines)
