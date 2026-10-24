# Plan: GET /progress

## Context
Add `GET /progress` returning how many rounds have been practised and the average total score, computed from `data/results.json`. No code written yet — this is the plan only.

What I found while reading the code:
- `data/results.json` is currently `[]`.
- `POST /score` (`app/main.py:38`) is a **stub**: it returns a placeholder and never calls `data.save_result`. Nothing writes results today, so `/progress` would always report zeros against real usage.
- `data.save_result(record: dict)` (`app/data.py:35`) appends a raw dict. The record shape is not defined anywhere.
- `scoring.compute_total` (`app/scoring.py:41`) has the seeded bug (`categories[1:]`), so any saved totals are too low.

## Files to change
1. `app/models.py` — add `ProgressResponse(BaseModel)`: `rounds_practised: int`, `average_total: float`. (Conventions: shapes are Pydantic models, not dicts.)
2. `app/data.py` — add `load_results() -> list[dict]` reading `results.json`. All disk access stays here. Reuse the same read pattern as `save_result`. Docstring, type hints, `from __future__` already present.
3. `app/scoring.py` — add `summarize_progress(results: list[dict]) -> ProgressResponse`: count = `len(results)`, average = mean of `total`, early return of zeros when empty. Keep it pure (no disk), so it's trivially testable. Name any constants (e.g. `EMPTY_AVERAGE = 0.0`, rounding digits).
4. `app/main.py` — add thin route: `@app.get("/progress")` → `scoring.summarize_progress(data.load_results())`. Needs `scoring` and `ProgressResponse` imports. No logic in the route.
5. `tests/test_progress.py` (new, one file per area) — see Verification.

Not touched: `data/questions.json`, `data/rubric.md`, `data/results.json` (CLAUDE.md guardrails), no new dependencies.

## Prerequisite (must come first)
**`POST /score` must be wired up before `/progress` is useful.** Today it is a stub (`app/main.py:38`) that never calls `data.save_result`, so `results.json` stays `[]` and `/progress` would always report zeros. Wiring it means: call `scoring.score_answer(request.answer)`, build a record (at least `round`, `question_id`, `total`, `max`), call `data.save_result(record)`, return the response. This is Module 3 "build" work, and the `compute_total` bug (`categories[1:]`) should be fixed alongside it or saved totals will be too low. I would do this as a separate, earlier task with its own diff and approval, not bundled into `/progress`. Doing it also pins down the record shape that `/progress` reads, which removes the riskiest assumption below.

## Order
0. **Prerequisite:** wire `POST /score` to `score_answer` + `save_result` (and fix `compute_total`), with its own tests. Separate diff, separate go-ahead.
1. `pytest -q` baseline.
2. Write failing tests first (`tests/test_progress.py`) with a fixture that redirects results to a temp file. Includes the empty-file test (step 6).
3. `ProgressResponse` in `models.py`.
4. `load_results` in `data.py`.
5. `summarize_progress` in `scoring.py` (non-empty path: count and mean).
6. **Empty-results guard (explicit step):** `summarize_progress` returns `rounds_practised=0, average_total=0.0` via an early return when `results` is empty, *before* any division. Own test: `test_progress_empty_results_returns_zeros`, which writes `[]` to the temp results file and asserts status 200 and both fields zero (no `ZeroDivisionError` / 500). Also a unit-level check calling `summarize_progress([])` directly.
7. Route in `main.py`.
8. `pytest -q` again; report results as-is.
Per CLAUDE.md, show each diff and wait for go-ahead before writing.

## What could break / easy to get wrong
- **Tests clobbering real data:** `data.py` does `from .config import DATA_DIR`, so the patch target is `app.data.DATA_DIR` (monkeypatch to `tmp_path`), not `app.config.DATA_DIR`. Getting this wrong makes tests read/write the real `data/results.json`.
- **Empty results → divide by zero.** Must return `0` / `0.0`, not 500.
- **Missing/malformed `total` key** in a record (record shape is undefined) → `KeyError` → 500.
- **Route ordering / name clash:** none expected, but the `round` param name shadows a builtin elsewhere — don't copy that.
- **Float output:** unrounded averages (e.g. 13.333333) are noisy; round to a named number of digits and test with `pytest.approx`.
- **Meaningless data today:** stub `/score` never saves and `compute_total` undercounts, so end-to-end the endpoint is "correct but empty/wrong" until Module 3 work lands. I'd not fix those here (smallest change), just flag them.

## Riskiest assumption
That **each record in `results.json` has a numeric `total` field and represents one practised round**. Nothing in the repo defines or writes that shape (`save_result` takes an untyped dict; `/score` never calls it). If the eventual writer uses a different key, or stores per-category scores only, `/progress` breaks silently or 500s.

Related open question: "rounds practised" could mean (a) number of scored attempts (`len(results)`) or (b) number of distinct round types (`decomposition`, `behavioral`, …). I'd default to (a) and name the field `rounds_practised` accordingly; (b) would need a `round` key in each record — which also isn't guaranteed.

## Verification
- `tests/test_progress.py` (all via `TestClient`, results file redirected to `tmp_path`):
  - `test_progress_empty_results_returns_zeros` — `[]` → `{rounds_practised: 0, average_total: 0.0}`, status 200 (the never-divide-by-zero guard).
  - `test_progress_counts_and_averages` — e.g. totals 10, 15, 20 → count 3, average 15.0; assert invariant `average == sum(totals)/count`.
  - `test_progress_single_result`.
- `pytest -q` before and after; all green.
- Manual: `uvicorn app.main:app --reload`, open `/docs`, call `GET /progress` → expect zeros on the current empty file.
