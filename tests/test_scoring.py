"""Tests for the scoring logic in app/scoring.py."""
from __future__ import annotations

from app.models import CategoryScore
from app.scoring import RUBRIC_CATEGORIES, compute_total

CATEGORY_SCORE = 3


def test_compute_total_sums_all_categories() -> None:
    categories = [
        CategoryScore(name=name, score=CATEGORY_SCORE, feedback="")
        for name in RUBRIC_CATEGORIES
    ]
    assert compute_total(categories) == sum(c.score for c in categories)
    assert compute_total(categories) == 12
