"""Tests for the scoring logic in app/scoring.py."""
from __future__ import annotations

import pytest

from app.models import CategoryScore
from app.scoring import RUBRIC_CATEGORIES, compute_total, format_scorecard

CATEGORY_SCORE = 3


def test_compute_total_sums_all_categories() -> None:
    categories = [
        CategoryScore(name=name, score=CATEGORY_SCORE, feedback="")
        for name in RUBRIC_CATEGORIES
    ]
    assert compute_total(categories) == sum(c.score for c in categories)
    assert compute_total(categories) == 12


def make_categories(scores: list[int]) -> list[CategoryScore]:
    return [
        CategoryScore(name=name, score=score, feedback="")
        for name, score in zip(RUBRIC_CATEGORIES, scores)
    ]


@pytest.mark.parametrize(
    ("scores", "total", "summary"),
    [
        ([5, 5, 5, 5], 20, "Strong answer - full marks"),
        ([5, 5, 5, 4], 19, "Strong answer"),
        ([4, 4, 4, 4], 16, "Strong answer"),
        ([4, 4, 4, 3], 15, "Solid, with gaps"),
        ([3, 3, 2, 2], 10, "Solid, with gaps"),
        ([3, 2, 2, 2], 9, "Needs work"),
        ([2, 1, 1, 1], 5, "Needs work"),
        ([1, 1, 1, 1], 4, "Needs significant work"),
        ([0, 0, 0, 0], 0, "Needs significant work"),
    ],
)
def test_format_scorecard_summary_bands(scores: list[int], total: int, summary: str) -> None:
    card = format_scorecard(make_categories(scores))
    assert card.total == total == sum(scores)
    assert card.max == 20
    assert card.summary == summary
