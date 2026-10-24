"""Tests for POST /score persistence. Results go to a temp file, never data/."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import data, scoring
from app.main import app

client = TestClient(app)

ANSWER = {"round": "decomposition", "question_id": "q1", "answer": "Ask, split, flag risks."}


@pytest.fixture
def results_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    path = tmp_path / "results.json"
    path.write_text("[]", encoding="utf-8")
    return path


def saved_records(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_score_saves_one_entry_per_rubric_category(results_file: Path) -> None:
    client.post("/score", json=ANSWER)
    (record,) = saved_records(results_file)
    names = [c["name"] for c in record["categories"]]
    assert names == scoring.RUBRIC_CATEGORIES


def test_score_saved_categories_match_response(results_file: Path) -> None:
    body = client.post("/score", json=ANSWER).json()
    (record,) = saved_records(results_file)
    expected = [{"name": c["name"], "score": c["score"]} for c in body["categories"]]
    assert record["categories"] == expected


def test_score_still_saves_existing_fields(results_file: Path) -> None:
    body = client.post("/score", json=ANSWER).json()
    (record,) = saved_records(results_file)
    assert record["round"] == ANSWER["round"]
    assert record["question_id"] == ANSWER["question_id"]
    assert record["total"] == body["total"]
    assert record["max"] == body["max"]
