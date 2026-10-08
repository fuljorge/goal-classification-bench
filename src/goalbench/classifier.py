"""Client for the System One `choice` question (Laya `laya-serve`, Strands Decider).

Every call sends one message and one `choice` question whose options are goal descriptions,
in the order given, and returns the probability of each option plus the wall-clock latency
measured on the client.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

QUESTION_ID = "goal"
INSTRUCTIONS = "Qual é o objetivo do cliente nesta mensagem?"


@dataclass(frozen=True)
class Answer:
    probabilities: dict[str, float]
    latency_ms: float


def parse_probabilities(answer: Any, keys: list[str]) -> dict[str, float]:
    """Normalised probability per option key; accepts index labels mapped by `legend`.

    A missing or empty distribution becomes uniform, so a malformed answer never favours an
    option (it is counted as a miss by argmax ties broken towards the first key).
    """
    raw = answer.get("probabilities") if isinstance(answer, dict) else None
    if not isinstance(raw, dict):
        return {k: 1.0 / len(keys) for k in keys}
    legend = answer.get("legend") if isinstance(answer.get("legend"), dict) else {}
    values: dict[str, float] = {}
    for label, value in raw.items():
        key = legend.get(str(label), label)
        if key in keys:
            values[key] = max(float(value), 0.0)
    total = sum(values.values())
    if total <= 0:
        return {k: 1.0 / len(keys) for k in keys}
    return {k: values.get(k, 0.0) / total for k in keys}


class ChoiceClient:
    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        model: str | None = None,
        lang: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.model = model
        self.lang = lang
        self.client = client or httpx.Client(timeout=120)

    def health(self) -> dict[str, Any]:
        response = self.client.get(f"{self.base_url}/health", headers=self.headers)
        response.raise_for_status()
        body = response.json()
        return body if isinstance(body, dict) else {}

    def choose(self, message: str, criteria: dict[str, str]) -> Answer:
        body: dict[str, Any] = {
            "state": {"body": message},
            "questions": {
                QUESTION_ID: {"type": "choice", "instructions": INSTRUCTIONS, "criteria": criteria}
            },
        }
        if self.model:
            body["model"] = self.model
        if self.lang:
            body["lang"] = self.lang
        started = time.perf_counter()
        response = self.client.post(
            f"{self.base_url}/v1/systemone", headers=self.headers, json=body
        )
        latency = (time.perf_counter() - started) * 1000
        response.raise_for_status()
        answer = response.json().get("answers", {}).get(QUESTION_ID)
        return Answer(parse_probabilities(answer, list(criteria)), latency)
