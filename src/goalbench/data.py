"""Dataset loading. One JSON object per line: key, name, description, examples, tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Goal:
    key: str
    name: str
    description: str
    examples: tuple[str, ...]
    tests: tuple[str, ...]


def load_goals(path: Path) -> list[Goal]:
    goals: list[Goal] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        try:
            goal = Goal(
                key=row["key"],
                name=row["name"],
                description=row["description"],
                examples=tuple(row["examples"]),
                tests=tuple(row["tests"]),
            )
        except KeyError as exc:
            raise ValueError(f"{path}:{number}: missing field {exc}") from exc
        goals.append(goal)
    keys = [g.key for g in goals]
    if len(set(keys)) != len(keys):
        raise ValueError(f"{path}: duplicate goal keys")
    examples = {e for g in goals for e in g.examples}
    if any(t in examples for g in goals for t in g.tests):
        raise ValueError(f"{path}: a test phrase also appears among the examples")
    return goals
