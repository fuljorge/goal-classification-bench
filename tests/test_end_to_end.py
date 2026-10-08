"""A full run against in-process fakes, then the offline report."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from goalbench.classifier import ChoiceClient, parse_probabilities
from goalbench.data import load_goals
from goalbench.embeddings import EmbeddingClient
from goalbench.pipeline import OptionOrder
from goalbench.report import load_run, markdown, paired, summary
from goalbench.run import collect

from .fakes import Policy, classifier_transport, embeddings_transport, first_option

TOKEN = "secret-token-value"
TOPICS = {
    "boleto": "boleto fatura conta pagar",
    "cartao": "cartao bloquear perdi roubado",
    "pix": "pix transferencia chave enviar",
    "senha": "senha acesso login esqueci",
}


def _dataset(tmp_path: Path) -> Path:
    lines = []
    for key, words in TOPICS.items():
        w = words.split()
        lines.append(
            json.dumps(
                {
                    "key": key,
                    "name": key,
                    "description": f"cliente fala de {words}",
                    "examples": [f"{w[i % 4]} {w[(i + 1) % 4]} exemplo {i}" for i in range(10)],
                    "tests": [f"{w[i % 4]} {w[(i + 2) % 4]} teste {i}" for i in range(5)],
                }
            )
        )
    path = tmp_path / "goals.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _collect(
    tmp_path: Path,
    order: OptionOrder,
    seed: int,
    calls: list[int] | None = None,
    policy: Policy = first_option,
    label: str = "first",
) -> Path:
    data = _dataset(tmp_path)
    embedder = EmbeddingClient(
        "http://emb/v1/embeddings",
        "qwen3-embedding-test",
        cache_path=tmp_path / "cache.npz",
        client=httpx.Client(transport=embeddings_transport(calls)),
    )
    classifier = ChoiceClient(
        "http://clf",
        token=TOKEN,
        lang="pt",
        client=httpx.Client(transport=classifier_transport(policy, TOKEN)),
    )
    return collect(
        load_goals(data),
        embedder,
        classifier,
        dataset_path=data,
        label=label,
        order=order,
        seed=seed,
        shortlist_size=3,
        out_dir=tmp_path / "results",
    )


def test_run_records_every_phrase_and_no_secret(tmp_path: Path) -> None:
    target = _collect(tmp_path, "random", 0)
    run = load_run(target)
    assert len(run.cv) == 40 and len(run.test) == 20
    assert all(
        len(r["shortlist"]) == 3 and sorted(r["presented"]) == sorted(r["shortlist"])
        for r in run.cv + run.test
    )
    assert {r["fold"] for r in run.cv} == set(range(5))
    for file in target.iterdir():
        assert TOKEN not in file.read_text(encoding="utf-8")


def test_cv_similarity_never_uses_the_phrase_fold(tmp_path: Path) -> None:
    run = load_run(_collect(tmp_path, "similarity", 0))
    # Each example scores below 1.0 against its own goal: its own vector is excluded.
    assert all(r["sims"][r["goal"]] < 0.999 for r in run.cv)


def test_position_baseline_exposes_a_position_prior(tmp_path: Path) -> None:
    by_similarity = summary(load_run(_collect(tmp_path, "similarity", 0)))
    reversed_ = summary(load_run(_collect(tmp_path, "reversed", 0)))
    alone = by_similarity["conditions"]["classifier_alone"]["accuracy"]
    assert alone == by_similarity["conditions"]["first_option"]["accuracy"]
    assert alone == by_similarity["conditions"]["embeddings_alone"]["accuracy"]
    assert by_similarity["position_bias"]["picks_first"] == 1.0
    assert reversed_["conditions"]["classifier_alone"]["accuracy"] < alone


def test_embedding_cache_avoids_second_call(tmp_path: Path) -> None:
    calls: list[int] = []
    _collect(tmp_path, "random", 0, calls)
    first = sum(calls)
    _collect(tmp_path, "random", 1, calls)
    assert sum(calls) == first


def last_option(message: str, keys: list[str]) -> dict[str, float]:
    return {k: v for k, v in zip(reversed(keys), first_option(message, keys).values(), strict=True)}


def test_report_and_paired_test(tmp_path: Path) -> None:
    runs = [
        load_run(_collect(tmp_path, "similarity", 0)),
        load_run(_collect(tmp_path, "similarity", 0, policy=last_option, label="last")),
    ]
    tests = paired(runs, "classifier_alone")
    assert len(tests) == 1
    assert tests[0]["only_first_correct"] > tests[0]["only_second_correct"]
    text = markdown([summary(r) for r in runs], tests)
    assert "McNemar" in text and "first_option" in text


def test_parse_probabilities_with_legend_and_garbage() -> None:
    keys = ["a", "b"]
    assert parse_probabilities(
        {"probabilities": {"0": 3, "1": 1}, "legend": {"0": "a", "1": "b"}}, keys
    ) == {"a": 0.75, "b": 0.25}
    assert parse_probabilities(None, keys) == {"a": 0.5, "b": 0.5}
    with pytest.raises(ValueError):
        parse_probabilities({"probabilities": {"a": "x"}}, keys)


def test_within_run_test_and_aggregate_across_seeds(tmp_path: Path) -> None:
    from goalbench.report import aggregate, within

    runs = [load_run(_collect(tmp_path, "random", seed)) for seed in (0, 1, 2)]
    tests = within(runs, "classifier_alone", "first_option")
    assert len(tests) == 3
    assert all(t["only_first_correct"] == 0 and t["only_second_correct"] == 0 for t in tests)
    groups = aggregate([summary(r) for r in runs])
    assert len(groups) == 1 and groups[0]["seeds"] == [0, 1, 2]
    alone = groups[0]["conditions"]["classifier_alone"]
    assert alone["min"] <= alone["mean"] <= alone["max"]


def test_paired_compares_only_runs_with_the_same_setting(tmp_path: Path) -> None:
    runs = [load_run(_collect(tmp_path, "random", seed)) for seed in (0, 1)]
    assert paired(runs, "classifier_alone") == []
