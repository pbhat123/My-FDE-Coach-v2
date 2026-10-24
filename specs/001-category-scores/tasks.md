# 001 — Tasks

Order matters: each task builds on the previous one. Every task is test-first
(failing test, then code), keeps `pytest -q` green at the end, and is one
reviewable commit. Criteria refer to `spec.md`.

## T1 — Add `weakest_category` to the response (always `null`)
- Add `weakest_category: str | None = None` to `ProgressResponse` in `app/models.py`.
- Update the three exact-equality assertions in `tests/test_progress.py` to
  include `"weakest_category": None`.
- Test: `/progress` with no results returns `weakest_category` as `null`.
- Covers: AC4 (no results yet), AC2 (existing fields unchanged)
- Done when: the response shape is final; behaviour is still unchanged.

## T2 — Save category scores on `POST /score`
- In `app/main.py`, add `"categories": [{"name", "score"}, ...]` to the record
  passed to `data.save_result`.
- New `tests/test_score_endpoint.py` with a fixture that points `data.DATA_DIR`
  at `tmp_path` (same pattern as `test_progress.py`).
- Tests: saved record has one `{name, score}` per rubric category and matches the
  response; `round`, `question_id`, `total`, `max` are still saved.
- Covers: AC1, AC2, AC11
- Done when: the real `data/results.json` is untouched after the test run
  (check `git status`).

## T3 — Compute the weakest category (happy path)
- In `app/scoring.py`, add a small helper that averages scores per category and
  returns the lowest; call it from `summarize_progress`.
- Tests: records with distinct averages return the expected category; the result
  is always in `RUBRIC_CATEGORIES`.
- Covers: AC3, AC8

## T4 — Old and mixed records
- Skip records with no `categories` key, but still count them in
  `rounds_practised` and `average_total`.
- Tests: only old records returns `null`; mixed old and new averages use only the
  new records; the counts still include the old ones.
- Covers: AC5, AC6 (AC4 also re-checked at the unit level)

## T5 — Tie-break by rubric order
- On equal lowest averages, return the category that appears first in
  `RUBRIC_CATEGORIES`.
- Tests: a two-way tie returns the earlier category; an all-equal tie returns the
  first rubric category. The result is the same regardless of record order.
- Covers: AC7

## T6 — Ignore unknown category names
- Names not in `RUBRIC_CATEGORIES` are ignored when computing averages.
- Tests: an unknown name with a very low score never wins; a record containing
  only unknown names counts as having no category data (`null`).
- Covers: AC12, AC8

## T7 — End-to-end check and quality gate
- Test: `POST /score` twice, then `GET /progress`, using the temp results file;
  `weakest_category` is a rubric name (the mock gives equal scores, so it is the
  first rubric category).
- Run `ruff`, `mypy`, `pytest -q`; confirm `git diff` shows no new dependencies
  and no changes to `data/`.
- Covers: AC9, AC10, AC11
- Done when: all three tools pass; any failure or tool that isn't installed is
  reported as it is.
