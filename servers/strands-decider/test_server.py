"""Tests of the Decider HTTP wrapper with a fake engine (no model, no GPU).

    uv run --with fastapi --with httpx --with pytest pytest servers/strands-decider
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient
from server import build_app

TOKEN = "test-token"
QUESTIONS = {
    "goal": {
        "type": "choice",
        "instructions": "Qual é o objetivo?",
        "criteria": {"get_invoice": "Segunda via", "cancel_plan": "Cancelar"},
    }
}


def fake_evaluate(body: dict[str, Any]) -> dict[str, Any]:
    if "questions" not in body:
        raise ValueError("questions is required")
    choice = "cancel_plan" if "cancelar" in str(body["state"]) else "get_invoice"
    other = "get_invoice" if choice == "cancel_plan" else "cancel_plan"
    answer = {"type": "choice", "choice": choice, "probabilities": {choice: 0.9, other: 0.1},
              "confidence": 0.9}
    return {"model": "fake", "answers": {"goal": answer},
            "usage": {"input_tokens": 10, "output_tokens": 0}}


def client(api_key: str | None = TOKEN) -> TestClient:
    return TestClient(build_app(fake_evaluate, api_key=api_key, alias="x", details={"device": "d"}))


AUTH = {"Authorization": f"Bearer {TOKEN}"}


def test_health_hides_details_without_token() -> None:
    assert client().get("/health").json() == {"status": "ok"}
    assert client().get("/health", headers=AUTH).json()["loaded"] == ["x"]


def test_question_routes_require_the_token() -> None:
    c = client()
    assert c.post("/v1/systemone", json={"state": "a", "questions": QUESTIONS}).status_code == 401
    wrong = {"Authorization": "Bearer other"}
    body = {"states": ["a"], "questions": QUESTIONS}
    assert c.post("/v1/systemone/batch", json=body, headers=wrong).status_code == 401


def test_single_accepts_laya_fields() -> None:
    body = {"state": {"body": "quero cancelar"}, "questions": QUESTIONS, "model": "m", "lang": "pt"}
    response = client().post("/v1/systemone", json=body, headers=AUTH)
    assert response.status_code == 200
    assert response.json()["answers"]["goal"]["choice"] == "cancel_plan"


def test_batch_keeps_order_and_sums_usage() -> None:
    body = {"states": [{"body": "segunda via"}, {"body": "quero cancelar"}], "questions": QUESTIONS}
    payload = client().post("/v1/systemone/batch", json=body, headers=AUTH).json()
    assert [r["answers"]["goal"]["choice"] for r in payload["results"]] == ["get_invoice",
                                                                           "cancel_plan"]
    assert payload["total_usage"] == {"input_tokens": 20, "output_tokens": 0}


def test_invalid_request_is_422() -> None:
    assert client().post("/v1/systemone", json={"state": "a"}, headers=AUTH).status_code == 422
