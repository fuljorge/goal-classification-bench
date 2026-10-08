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
    # analyze() is deterministic; its result is kept so every test reuses one fit per run.
    analysis: dict[str, Result] | None = field(default=None, repr=False, compare=False)

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
    if run.analysis is None:
        run.analysis = _analyze(run)
    return run.analysis


def _analyze(run: Run) -> dict[str, Result]:
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
        "dataset": run.meta["dataset"]["file"],
        "embedding_model": run.meta["embedding"]["model"],
        "option_order": run.meta["protocol"]["option_order"],
        "seed": run.meta["protocol"]["seed"],
        "conditions": {k: v.as_dict() for k, v in results.items()},
        "position_bias": position_bias(run),
        "classifier_latency": latency(run),
    }


def _setting(run: Run) -> tuple[str, str, str, int]:
    protocol = run.meta["protocol"]
    return (
        run.meta["dataset"]["sha256"],
        run.meta["embedding"]["model"],
        protocol["option_order"],
        protocol["seed"],
    )


def _mcnemar(a: list[bool], b: list[bool]) -> dict[str, Any]:
    only_a = sum(x and not y for x, y in zip(a, b, strict=True))
    only_b = sum(y and not x for x, y in zip(a, b, strict=True))
    return {
        "only_first_correct": only_a,
        "only_second_correct": only_b,
        "p_value": mcnemar_exact(only_a, only_b),
    }


def paired(runs: list[Run], condition: str) -> list[dict[str, Any]]:
    """Exact McNemar test between runs of different deciders under the same setting.

    Two runs are compared only when they share the dataset, the embedding model, the option
    order and the seed, so that they saw the same shortlists, folds and option permutations.
    """
    out = []
    for first, second in combinations(runs, 2):
        if _setting(first) != _setting(second):
            continue
        if [(r["goal"], r["text"]) for r in first.test] != [
            (r["goal"], r["text"]) for r in second.test
        ]:
            raise ValueError(f"{first.name} and {second.name} have different test phrases")
        a = analyze(first)[condition].correct
        b = analyze(second)[condition].correct
        out.append(
            {"condition": condition, "first": first.name, "second": second.name, **_mcnemar(a, b)}
        )
    return out


def crosslingual(runs: list[Run], condition: str) -> list[dict[str, Any]]:
    """Exact McNemar test between the same decider on two parallel datasets.

    Runs are paired when they share the decider label, the embedding model, the option order
    and the seed but use different datasets. Phrases are aligned by position: parallel
    datasets list the same goals in the same order, with the i-th phrase of each goal being
    a translation of the other's.
    """
    out = []
    for first, second in combinations(runs, 2):
        a_set, b_set = _setting(first), _setting(second)
        if a_set[0] == b_set[0] or a_set[1:] != b_set[1:]:
            continue
        if first.meta["label"] != second.meta["label"]:
            continue
        a_goals = [r["goal"] for r in first.test]
        b_goals = [r["goal"] for r in second.test]
        boundaries = (
            [i for i in range(1, len(a_goals)) if a_goals[i] != a_goals[i - 1]],
            [i for i in range(1, len(b_goals)) if b_goals[i] != b_goals[i - 1]],
        )
        if len(a_goals) != len(b_goals) or boundaries[0] != boundaries[1]:
            raise ValueError(f"{first.name} and {second.name} are not parallel datasets")
        a = analyze(first)[condition].correct
        b = analyze(second)[condition].correct
        out.append(
            {
                "condition": condition,
                "first": f"{first.meta['dataset']['file']}/{first.name}",
                "second": f"{second.meta['dataset']['file']}/{second.name}",
                **_mcnemar(a, b),
            }
        )
    return out


def within(runs: list[Run], first: str, second: str) -> list[dict[str, Any]]:
    """Exact McNemar test between two conditions of the same run (same phrases)."""
    out = []
    for run in runs:
        results = analyze(run)
        out.append(
            {
                "run": run.name,
                "first": first,
                "second": second,
                **_mcnemar(results[first].correct, results[second].correct),
            }
        )
    return out


def aggregate(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mean, sample standard deviation, min and max of each condition across seeds."""
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for s in summaries:
        key = (s["dataset"], s["label"], s["embedding_model"], s["option_order"])
        groups.setdefault(key, []).append(s)
    out = []
    for (dataset, label, model, order), members in groups.items():
        row: dict[str, Any] = {
            "dataset": dataset,
            "label": label,
            "embedding_model": model,
            "option_order": order,
            "seeds": sorted(m["seed"] for m in members),
            "conditions": {},
        }
        for condition in CONDITIONS:
            values = [m["conditions"][condition]["accuracy"] for m in members]
            row["conditions"][condition] = {
                "mean": statistics.fmean(values),
                "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
                "min": min(values),
                "max": max(values),
            }
        row["picks_first_mean"] = statistics.fmean(
            m["position_bias"]["picks_first"] for m in members
        )
        row["latency_p95_ms_mean"] = statistics.fmean(
            m["classifier_latency"]["p95_ms"] for m in members
        )
        out.append(row)
    return out


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def markdown(
    summaries: list[dict[str, Any]],
    tests: list[dict[str, Any]],
    within_tests: list[dict[str, Any]] | None = None,
    aggregates: list[dict[str, Any]] | None = None,
) -> str:
    lines: list[str] = []
    if aggregates:
        lines += [
            "| Dataset | Decider | Embeddings | Order | Seeds | " + " | ".join(CONDITIONS) + " |",
            "|---" * (len(CONDITIONS) + 5) + "|",
        ]
        for g in aggregates:
            cells = [
                f"{_pct(c['mean'])} ± {100 * c['sd']:.1f}"
                for c in (g["conditions"][k] for k in CONDITIONS)
            ]
            seeds = ",".join(str(s) for s in g["seeds"])
            lines.append(
                f"| {g['dataset']} | {g['label']} | {g['embedding_model']} | {g['option_order']}"
                f" | {seeds} | " + " | ".join(cells) + " |"
            )
        lines.append("")
    lines += [
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
    if within_tests:
        lines += [
            "",
            "| Run | First | Second | Only first | Only second | McNemar p |",
            "|---|---|---|---|---|---|",
        ]
        for t in within_tests:
            lines.append(
                f"| {t['run']} | {t['first']} | {t['second']} | {t['only_first_correct']}"
                f" | {t['only_second_correct']} | {t['p_value']:.4f} |"
            )
    lines += ["", "Conditions:"] + [f"- `{k}`: {v}" for k, v in DESCRIPTIONS.items()]
    return "\n".join(lines)
