"""Tests for GET /progress. Results are redirected to a temp file, never data/."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import data, scoring
from app.main import app

client = TestClient(app)

EVEN_SCORES = {name: 4 for name in scoring.RUBRIC_CATEGORIES}
OLD_RECORD = {"round": "decomposition", "question_id": "q", "total": 20, "max": 20}


@pytest.fixture
def results_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    path = tmp_path / "results.json"
    path.write_text("[]", encoding="utf-8")
    return path


def write_totals(path: Path, totals: list[int]) -> None:
    records = [
        {"round": "decomposition", "question_id": "q", "total": t, "max": 20} for t in totals
    ]
    path.write_text(json.dumps(records), encoding="utf-8")


def make_record(scores: dict[str, int]) -> dict:
    """A saved result whose category scores are given by name."""
    return {
        "round": "decomposition",
        "question_id": "q",
        "total": sum(scores.values()),
        "max": 20,
        "categories": [{"name": n, "score": s} for n, s in scores.items()],
    }


def test_progress_empty_results_returns_zeros(results_file: Path) -> None:
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {
        "rounds_practised": 0,
        "average_total": 0.0,
        "weakest_category": None,
    }


def test_summarize_progress_empty_list_does_not_divide_by_zero() -> None:
    result = scoring.summarize_progress([])
    assert result.rounds_practised == 0
    assert result.average_total == 0.0


def test_progress_single_result(results_file: Path) -> None:
    write_totals(results_file, [12])
    body = client.get("/progress").json()
    assert body == {
        "rounds_practised": 1,
        "average_total": 12.0,
        "weakest_category": None,
    }


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


def test_summarize_progress_weakest_category_has_lowest_average() -> None:
    results = [
        make_record(
            {
                "Clarifying questions": 4,
                "Decomposition": 3,
                "Risk identification": 1,
                "Communication": 4,
            }
        ),
        make_record(
            {
                "Clarifying questions": 2,
                "Decomposition": 5,
                "Risk identification": 3,
                "Communication": 4,
            }
        ),
    ]
    # Averages: Clarifying 3.0, Decomposition 4.0, Risk 2.0, Communication 4.0
    assert scoring.summarize_progress(results).weakest_category == "Risk identification"


def test_summarize_progress_weakest_category_is_a_rubric_category() -> None:
    results = [make_record({name: 3 for name in scoring.RUBRIC_CATEGORIES})]
    weakest = scoring.summarize_progress(results).weakest_category
    assert weakest in scoring.RUBRIC_CATEGORIES


def test_progress_endpoint_returns_weakest_category(results_file: Path) -> None:
    record = make_record(
        {
            "Clarifying questions": 4,
            "Decomposition": 2,
            "Risk identification": 4,
            "Communication": 4,
        }
    )
    results_file.write_text(json.dumps([record]), encoding="utf-8")
    assert client.get("/progress").json()["weakest_category"] == "Decomposition"


# --- T4: records without category data -------------------------------------


def test_weakest_category_is_none_when_no_record_has_category_data() -> None:
    results = [OLD_RECORD, {**OLD_RECORD, "categories": []}]
    result = scoring.summarize_progress(results)
    assert result.weakest_category is None
    assert result.rounds_practised == len(results)


def test_weakest_category_ignores_old_records_but_still_counts_them() -> None:
    new_record = make_record({**EVEN_SCORES, "Communication": 1})  # total 13
    result = scoring.summarize_progress([OLD_RECORD, new_record])
    assert result.weakest_category == "Communication"
    assert result.rounds_practised == 2
    assert result.average_total == 16.5  # (20 + 13) / 2
