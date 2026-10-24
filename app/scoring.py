"""Scoring logic: turn a candidate's answer into a rubric-based scorecard.

>>> THIS FILE IS WHERE MOST OF THE WORKSHOP HAPPENS. <<<

In this START state, POST /score is not wired to any of it yet (see app/main.py).
During Module 3 you will, with Claude Code:
  * build    -> implement score_with_openai() and wire /score to score_answer()
  * test     -> write tests pinning  total == sum(category scores)
  * debug    -> those tests reveal the BUG in compute_total()      (marked below)
  * refactor -> clean up the messy format_scorecard()              (marked below)
"""
from __future__ import annotations

from .config import USE_MOCK
from .models import CategoryScore, ProgressResponse, ScoreResponse

# The four things every answer is scored on (mirrors data/rubric.md).
RUBRIC_CATEGORIES = [
    "Clarifying questions",
    "Decomposition",
    "Risk identification",
    "Communication",
]

EMPTY_AVERAGE = 0.0
AVERAGE_DECIMALS = 1

FULL_MARKS_TOTAL = 20
FULL_MARKS_SUMMARY = "Strong answer - full marks"
# (minimum total, summary), checked from the highest band down.
SUMMARY_BANDS = [
    (16, "Strong answer"),
    (10, "Solid, with gaps"),
    (5, "Needs work"),
]
LOWEST_SUMMARY = "Needs significant work"


def score_mock(answer: str) -> list[CategoryScore]:
    """A tiny deterministic scorer used when there is no OpenAI key.

    Intentionally simple: longer, more structured answers score a little higher.
    The workshop is about the *workflow*, not about building a clever scorer.
    """
    length_signal = min(len(answer) // 120, 5)  # 0..5 by answer length
    structure_signal = min(answer.count("\n") + 1, 5)  # 0..5 by line breaks
    base = max(1, (length_signal + structure_signal) // 2)
    return [
        CategoryScore(name=name, score=base, feedback=f"Auto-estimate for '{name}'.")
        for name in RUBRIC_CATEGORIES
    ]


def compute_total(categories: list[CategoryScore]) -> int:
    """Sum the scores of all categories into a single total."""
    total = 0
    for category in categories:
        total += category.score
    return total


def summarize_total(total: int) -> str:
    """Return the summary band for a total score."""
    if total == FULL_MARKS_TOTAL:
        return FULL_MARKS_SUMMARY
    for minimum, summary in SUMMARY_BANDS:
        if total >= minimum:
            return summary
    return LOWEST_SUMMARY


def format_scorecard(categories: list[CategoryScore]) -> ScoreResponse:
    """Assemble the final ScoreResponse from the category scores."""
    total = compute_total(categories)
    maximum = sum(c.max for c in categories)
    return ScoreResponse(
        total=total, max=maximum, categories=categories, summary=summarize_total(total)
    )


def score_with_openai(answer: str) -> list[CategoryScore]:
    """Score using the real OpenAI API.

    *** STUB — Module 3 (build) ***
    Implement this to send the rubric (data/rubric.md) plus the candidate's
    answer to OpenAI using config.MODEL_ID, ask for JSON back, and parse it into
    one CategoryScore per rubric category. For now it just calls the mock so the
    app keeps working.
    """
    # TODO(workshop): call the OpenAI API here and parse the JSON response.
    return score_mock(answer)


def score_answer(answer: str) -> ScoreResponse:
    """Score one answer end to end (mock offline, OpenAI when a key is set)."""
    categories = score_with_openai(answer) if not USE_MOCK else score_mock(answer)
    return format_scorecard(categories)


def summarize_progress(results: list[dict]) -> ProgressResponse:
    """Count the practised rounds and average their total scores."""
    if not results:
        return ProgressResponse(rounds_practised=0, average_total=EMPTY_AVERAGE)
    average = sum(r["total"] for r in results) / len(results)
    return ProgressResponse(
        rounds_practised=len(results),
        average_total=round(average, AVERAGE_DECIMALS),
    )
