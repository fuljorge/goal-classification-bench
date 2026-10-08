"""Command line: `goalbench run` collects one run; `goalbench report` analyses runs.

Secrets are read from environment variables whose names are given on the command line, so
they never appear in shell history, run files or reports.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .classifier import INSTRUCTIONS, INSTRUCTIONS_EN, ChoiceClient
from .data import load_goals
from .embeddings import EmbeddingClient
from .pipeline import ORDERS, SHORTLIST
from .report import (
    CONDITIONS,
    aggregate,
    crosslingual,
    load_run,
    markdown,
    paired,
    summary,
    within,
)
from .run import collect

DEFAULT_DATA = Path("data/goals_ptbr.jsonl")


def _run(args: argparse.Namespace) -> int:
    goals = load_goals(args.data)
    cache = args.embeddings_cache or Path(".cache") / f"embeddings-{args.embeddings_model}.npz"
    embedder = EmbeddingClient(
        args.embeddings_url,
        args.embeddings_model,
        api_key=os.environ.get(args.embeddings_key_env) or None,
        cache_path=cache,
    )
    classifier = ChoiceClient(
        args.classifier_url,
        token=os.environ.get(args.classifier_token_env) or None,
        model=args.classifier_model,
        lang=args.lang,
        instructions=args.instructions,
    )
    for seed in args.seed:
        target = collect(
            goals,
            embedder,
            classifier,
            dataset_path=args.data,
            label=args.label,
            order=args.order,
            seed=seed,
            shortlist_size=args.shortlist,
            out_dir=args.out,
            progress=lambda done, total: print(f"\r{done}/{total}", end="", file=sys.stderr),
        )
        print(f"\n{target}", file=sys.stderr)
    return 0


def _report(args: argparse.Namespace) -> int:
    runs = [load_run(p) for p in args.runs]
    summaries = [summary(r) for r in runs]
    tests = [t for c in args.compare for t in paired(runs, c)] if len(runs) > 1 else []
    if args.cross_dataset:
        tests += [t for c in args.compare for t in crosslingual(runs, c)]
    within_tests = [t for pair in args.within for t in within(runs, *pair.split(":", 1))]
    aggregates = aggregate(summaries)
    if args.json:
        payload = {
            "runs": summaries,
            "aggregates": aggregates,
            "paired_tests": tests,
            "within_tests": within_tests,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(markdown(summaries, tests, within_tests, aggregates))
    return 0


def _condition_pair(value: str) -> str:
    first, sep, second = value.partition(":")
    if not sep or first not in CONDITIONS or second not in CONDITIONS:
        raise argparse.ArgumentTypeError(f"expected CONDITION:CONDITION, got {value!r}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="goalbench", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="collect one run per seed")
    run.add_argument("--data", type=Path, default=DEFAULT_DATA)
    run.add_argument(
        "--embeddings-url",
        required=True,
        help="full URL of an OpenAI-compatible /embeddings endpoint",
    )
    run.add_argument("--embeddings-model", required=True)
    run.add_argument("--embeddings-key-env", default="GOALBENCH_EMBEDDINGS_KEY")
    run.add_argument("--embeddings-cache", type=Path)
    run.add_argument("--classifier-url", required=True, help="base URL of the System One server")
    run.add_argument("--classifier-token-env", default="GOALBENCH_CLASSIFIER_TOKEN")
    run.add_argument("--classifier-model", help='value of the "model" field (Laya: multilingual)')
    run.add_argument("--lang", help='value of the "lang" field (Laya: pt)')
    run.add_argument(
        "--instructions",
        default=INSTRUCTIONS,
        help=f"question sent with every choice (default: Portuguese; for the English dataset: "
        f"{INSTRUCTIONS_EN!r})",
    )
    run.add_argument("--label", required=True, help="name of the classifier in the results")
    run.add_argument("--order", choices=ORDERS, default="random")
    run.add_argument("--seed", type=int, nargs="+", default=[0])
    run.add_argument("--shortlist", type=int, default=SHORTLIST)
    run.add_argument("--out", type=Path, default=Path("results"))
    run.set_defaults(func=_run)

    report = sub.add_parser("report", help="analyse collected runs")
    report.add_argument("runs", type=Path, nargs="+")
    report.add_argument(
        "--compare",
        nargs="+",
        choices=CONDITIONS,
        default=["classifier_alone", "fitted_grid_with_zero"],
    )
    report.add_argument(
        "--within",
        nargs="+",
        type=_condition_pair,
        default=["fitted_grid_with_zero:embeddings_alone", "classifier_alone:embeddings_alone"],
        help="pairs of conditions compared inside each run (CONDITION:CONDITION)",
    )
    report.add_argument(
        "--cross-dataset",
        action="store_true",
        help="also compare each decider across parallel datasets (phrases aligned by position)",
    )
    report.add_argument("--json", action="store_true")
    report.set_defaults(func=_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
