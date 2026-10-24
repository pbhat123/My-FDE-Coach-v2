# CLAUDE.md — FDE Interview Prep Assistant

> Claude Code reads this file at the start of every session. It's how you onboard
> the agent to THIS project — the way a senior engineer briefs a new hire.
>
> 🚧 This is a **skeleton on purpose**. You complete the TODO sections in
> **Module 1**, after touring the codebase with Claude Code.

## What we're building
A small FastAPI app that runs mock Forward Deployed Engineer interviews and
scores the answers against a rubric (4 categories, each 0–5, max total 20).
Favour **clarity over cleverness** — every line should be explainable in an interview.

Flow: client picks a round → GET a question → POST an answer to /score →
get a per-category scorecard, which is saved to `data/results.json`.

## Stack
- Python 3.11+, **FastAPI** (served by uvicorn), **Pydantic v2**
- Data: plain **JSON files** in `data/` — no database
- Scoring: an offline **mock** scorer, or the **OpenAI API** when a key is set
  (the model id lives in one constant, `app/config.MODEL_ID`)
- Tests: **pytest** — never call the network in a test

## Project layout
- `app/main.py`     — FastAPI routes only; no business logic
- `app/models.py`   — Pydantic request/response schemas
- `app/data.py`     — ALL disk access (questions, rubric, results). Nothing else reads `data/`
- `app/scoring.py`  — scoring logic: mock scorer, OpenAI scorer, total, scorecard formatting
- `app/config.py`   — paths, `MODEL_ID`, `USE_MOCK`. The only place that reads env vars
- `data/`           — `questions.json`, `rubric.md`, `results.json`
- `resources/`      — study guides (one per round type)
- `tests/`          — pytest; one file per area

## Conventions
- Type hints on every function; `from __future__ import annotations` at the top of each module
- Short docstring on every public function: what, not how
- Request/response shapes are Pydantic models in `models.py`, not raw dicts
  (`save_result` is the one exception today)
- Routes stay thin: validate → call a function in `data.py`/`scoring.py` → return
- Rubric category names live in `scoring.RUBRIC_CATEGORIES` and must match `data/rubric.md`
- No magic numbers or strings in logic — name them as constants
- Keep functions small and flat; prefer early returns over nested if/else
- Tests: name them `test_<behaviour>`; assert invariants (e.g. `total == sum(scores)`),
  not just status codes

## Guardrails for you, the agent
- **Never commit `.env`.** Keep it listed in `.gitignore`, never `git add` it, and
  never stage files with `git add -A` / `git add .` without checking what's included.
- **Never read or print `.env` or any API key.** Only edit `.env.example`.
- **Show me the diff before applying changes.** Propose edits as a diff and wait for
  my go-ahead before writing to any file in the repo.
- **Never call the network in tests.** Tests run in mock mode; monkeypatch anything else.
- Don't hard-code the model id anywhere except `config.MODEL_ID`.
- Don't add dependencies, a database, or a new framework without asking first.
- Don't touch `data/questions.json` or `data/rubric.md` unless asked — they define the product.
- Debugging: write a failing test first, list ranked hypotheses, and only then change code.
- Refactoring: run `pytest -q` before and after; keep tests green at every step.
- Make the smallest change that solves the task; don't reformat unrelated code.
- Report test results as they are — if something fails or was not run, say so.
- Ask before: deleting files, overwriting `data/results.json`, or running anything that costs money.

## How to run
```
python -m venv .venv
source .venv/bin/activate         # macOS/Linux  (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env              # optional — only needed for real OpenAI scoring
uvicorn app.main:app --reload     # open http://127.0.0.1:8000/docs
pytest -q
```
