---
description: Summarise practice progress from data/results.json
allowed-tools: Read
---

Summarise my interview practice from `data/results.json`. Read-only: don't edit any file.

1. Read `data/results.json`. It is a JSON list of records with
   `round`, `question_id`, `total` and `max`.
2. If the file is missing or the list is empty, reply only:
   "No results yet. Run a mock round first." Then stop.
3. Otherwise report:
   - **Rounds practised:** the number of records.
   - **Average total:** mean of `total`, shown as `X.X/20`, rounded to one decimal.
   - **Weakest rubric category:** if any record has a `categories` list, average
     each category's `score` and name the lowest. If no record has per-category
     scores, say "Not available: results only store totals" and instead name the
     round type with the lowest average `total` as the weakest area.
   - **Focus next:** one concrete suggestion tied to the weakest area. For a
     category, point to the matching bullet in `data/rubric.md`. For a round, point
     to its guide in `resources/`.

Compute the numbers from the file; don't estimate. Keep the reply under 10 lines.
