# 001 — Category scores & weakest category

## Why
`/progress` only reports an overall average, so a candidate can't tell *what* to
practise. Saving per-category scores lets us point at the weakest rubric
category (e.g. "Risk identification").

## What changes for the user
- `POST /score`: response is unchanged. The saved result now also records each
  category's name and score.
- `GET /progress`: response gains `weakest_category: str | None`, the rubric
  category with the lowest average score across saved results.

## Decisions
- Saved record gains `"categories": [{"name": "...", "score": N}, ...]`
  (name + score only; no feedback text).
- A category's average uses only the records that contain data for it.
- Ties are broken by the order of `scoring.RUBRIC_CATEGORIES` (first wins),
  so the answer is deterministic.
- Old records without category data are skipped for `weakest_category`.

## Riskiest assumption
Saved category names exactly match `RUBRIC_CATEGORIES`. This matters when OpenAI
scoring is on, because the model could return a differently spelled or cased
name. Criterion 12 limits the damage: unknown names are ignored, not crashed on.

## Acceptance criteria
1. After `POST /score`, the new record in `data/results.json` has a
   `categories` list with one `{name, score}` entry per rubric category, and
   each entry matches the scorecard returned in the response.
2. Existing record fields (`round`, `question_id`, `total`, `max`) are unchanged.
3. `GET /progress` returns `weakest_category` equal to the category with the
   lowest average score across all saved results.
4. **No results yet:** `weakest_category` is `null`; `rounds_practised` is 0 and
   `average_total` is 0.0 as today; status is 200.
5. **Old records without category data:** records with no `categories` key, or
   an empty `categories` list, are skipped for `weakest_category` but still count
   toward `rounds_practised` and `average_total`. If *no* record has category
   data, `weakest_category` is `null`.
6. **Mixed old and new records:** averages are computed only from records that
   have category data.
7. **Ties:** if two or more categories share the lowest average, the one that
   appears first in `RUBRIC_CATEGORIES` is returned.
8. The returned value is always a name from `RUBRIC_CATEGORIES` or `null`.
9. Tests run in mock mode and never call the network.
10. `ruff` and `mypy` are clean, `pytest -q` is green, and no new dependencies
    are added.
11. Tests for `POST /score` use a temporary results file and never write to the
    real `data/results.json`.
12. Saved category names that are not in `RUBRIC_CATEGORIES` are ignored when
    computing `weakest_category`.

## Reads / writes
- Reads: `data/results.json` (via `data.load_results`)
- Writes: `data/results.json` (via `data.save_result`)
- Code touched: `app/main.py` (pass categories to `save_result`),
  `app/models.py` (`ProgressResponse`), `app/scoring.py` (`summarize_progress`),
  `tests/test_progress.py`, `tests/test_basic.py`
- Not touched: `data/questions.json`, `data/rubric.md`

## Out of scope
- Backfilling or migrating old records
- Saving per-category feedback text
- Per-round or time-windowed weakest category
- Returning all tied categories, or the averages themselves
- Any new dependency, database, or change to the scoring logic
