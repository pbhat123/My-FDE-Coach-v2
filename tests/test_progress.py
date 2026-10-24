"""Tests for GET /progress. Results are redirected to a temp file, never data/."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import data, scoring
from app.main import app

client = TestClient(app)


@pytest.fixture
def results_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    path = tmp_path / "results.json"
    path.write_text("[]", encoding="utf-8")
    return path


def write_totals(path: Path, totals: list[int]) -> None:
    records = [{"round": "decomposition", "question_id": "q", "total": t, "max": 20} for t in totals]
    path.write_text(json.dumps(records), encoding="utf-8")


def test_progress_empty_results_returns_zeros(results_file: Path) -> None:
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": 0.0}


def test_summarize_progress_empty_list_does_not_divide_by_zero() -> None:
    result = scoring.summarize_progress([])
    assert result.rounds_practised == 0
    assert result.average_total == 0.0


def test_progress_single_result(results_file: Path) -> None:
    write_totals(results_file, [12])
    body = client.get("/progress").json()
    assert body == {"rounds_practised": 1, "average_total": 12.0}


def test_progress_counts_and_averages(results_file: Path) -> None:
    totals = [10, 15, 20]
    write_totals(results_file, totals)
    body = client.get("/progress").json()
    assert body["rounds_practised"] == len(totals)
    assert body["average_total"] == pytest.approx(sum(totals) / len(totals))


def test_progress_rounds_average_to_one_decimal(results_file: Path) -> None:
    write_totals(results_file, [10, 11, 11])
    body = client.get("/progress").json()
    assert body["average_total"] == 10.7
